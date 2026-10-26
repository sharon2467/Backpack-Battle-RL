# Narrow saved monitor/wrapper association diagnosis

402's initial binder incorrectly required every generic monitor field to equal the later wrapper record. Root checked actual differences against pinned363execute_process:monitor is written first;the wrapper changes scope/count/parse_only/clean flag and augments limits. Only exact source-defined transformations were permitted;all other values/types stay equal. Native ERROR-marker presence explains clean=false and remains unresolved as an operational limitation,not relabelled benign/clean. Supplement scope permits only ERROR presence and three parse collector-marker booleans,not log lines/business data.

Original failed binder/trace and later independently sealed corrections are in402. This narrow source/metadata diagnosis ran no SUT/helper/model/native. Root's own owner-list/dictionary iteration error is also preserved;normalizing the actual dictionary format changed no evidence or inputs.
