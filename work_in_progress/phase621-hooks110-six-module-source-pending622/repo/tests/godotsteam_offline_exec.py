"""Restrict this process and descendants to UNIX sockets; never change host networking."""
import ctypes
import errno
import json
import os
from pathlib import Path
import resource
import socket
import subprocess
import sys


class Compare(ctypes.Structure):
    _fields_ = [("arg", ctypes.c_uint), ("op", ctypes.c_uint),
                ("datum_a", ctypes.c_uint64), ("datum_b", ctypes.c_uint64)]


def install_filter():
    lib = ctypes.CDLL("libseccomp.so.2", use_errno=True)
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    lib.seccomp_rule_add_array.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                          ctypes.c_int, ctypes.c_uint, ctypes.POINTER(Compare)]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = lib.seccomp_init(0x7FFF0000)  # SCMP_ACT_ALLOW
    if not ctx:
        raise RuntimeError("seccomp_init failed")
    try:
        for name in (b"socket", b"socketpair", b"io_uring_setup"):
            nr = lib.seccomp_syscall_resolve_name(name)
            if nr < 0:
                raise RuntimeError("Unknown syscall: " + name.decode())
            cmp = Compare(0, 1, socket.AF_UNIX, 0)  # SCMP_CMP_NE
            count = 0 if name == b"io_uring_setup" else 1
            rc = lib.seccomp_rule_add_array(ctx, 0x00050000 | errno.EPERM,
                                            nr, count, ctypes.byref(cmp) if count else None)
            if rc != 0:
                raise RuntimeError("seccomp rule failed: " + str(rc))
        rc = lib.seccomp_load(ctx)
        if rc != 0:
            raise RuntimeError("seccomp_load failed: " + str(rc))
    finally:
        lib.seccomp_release(ctx)


def self_test(inherited_only=False):
    checks = []
    for family, kind in [(socket.AF_INET, socket.SOCK_STREAM),
                         (socket.AF_INET, socket.SOCK_DGRAM),
                         (socket.AF_INET6, socket.SOCK_STREAM),
                         (socket.AF_INET6, socket.SOCK_DGRAM),
                         (socket.AF_PACKET, socket.SOCK_RAW),
                         (socket.AF_NETLINK, socket.SOCK_RAW)]:
        try:
            s = socket.socket(family, kind)
        except OSError as exc:
            checks.append({"family": int(family), "type": int(kind),
                           "errno": exc.errno, "pass": exc.errno == errno.EPERM})
        else:
            s.close()
            checks.append({"family": int(family), "type": int(kind), "pass": False})
    a, b = socket.socketpair()
    a.send(b"local-only")
    unix_ok = b.recv(10) == b"local-only"
    a.close()
    b.close()
    result = {"checks": checks, "unix_socket_pass": unix_ok,
              "status": "PASS" if unix_ok and all(c["pass"] for c in checks) else "FAIL"}
    if not inherited_only:
        # Import only the checks after exec; the child does NOT install another filter.
        code = ("import sys; sys.path.insert(0, " + repr(str(Path(__file__).parent)) + "); "
                "from godotsteam_offline_exec import self_test; sys.exit(self_test(inherited_only=True))")
        child = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                               close_fds=True, timeout=5)
        result["exec_inheritance"] = json.loads(child.stdout)
        if child.returncode != 0 or result["exec_inheritance"]["status"] != "PASS":
            result["status"] = "FAIL"
    print(json.dumps(result), flush=True)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    # No inherited network FDs survive; stdout/stderr are redirected to regular files by the runner.
    fd_limit = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
    os.closerange(3, fd_limit if fd_limit != resource.RLIM_INFINITY else 1048576)
    install_filter()
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    if len(sys.argv) < 2:
        raise SystemExit("Usage: godotsteam_offline_exec.py COMMAND [ARGS...]")
    os.execvpe(sys.argv[1], sys.argv[1:], os.environ)
