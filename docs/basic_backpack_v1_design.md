# 基础背包 V1 设计

## 目标

V1 只解决一个最小闭环：

```text
物品放置列表 -> 63 格占用矩阵 -> 星位关联
```

本阶段使用真实背包总区域：`width = 9`，`height = 7`，共 `63` 格。

V1 暂时不引入背包格或袋子解锁规则，默认 63 格全部可用。

## 输入

背包输入是一个物品放置列表：

```python
placements = [
    {
        "item_id": "stone",
        "x": 0,
        "y": 0,
        "rotation": 0,
    }
]
```

字段含义：

- `item_id`：物品定义 id。
- `x`：物品参考点的列坐标。
- `y`：物品参考点的行坐标。
- `rotation`：旋转状态，只允许 `0`、`90`、`180`、`270`。

坐标约定：

- `x` 向右增加。
- `y` 向上增加。
- 背包左下角格子是 `(0, 0)`。
- 背包右上角格子是 `(8, 6)`。
- 有效坐标范围是 `0 <= x < 9`，`0 <= y < 7`。
- 参考点只是计算相对坐标的锚点，本身不需要显式出现在 `shape_cells` 或 marker cells 中。

## 物品定义

V1 的物品数据先手写最小样例，存放在 `data/item_catalog_v1.json`，不批量导入真实 wiki 数据。

程序启动时读取这个 JSON，得到 `item_catalog`。

字段含义：

- `item_id`：物品定义 id。
- `shape_cells`：未旋转时，物品占用格子相对于参考点的位置。
- `star_cells`：未旋转时，物品星位相对于参考点的位置。
- `diamond_cells`：未旋转时，物品菱形位相对于参考点的位置。
- `triangle_cells`：未旋转时，物品三角位相对于参考点的位置。
- `star_cells_by_rotation`：特殊物品使用；直接穷举每个旋转状态下的星位相对坐标。

`shape_cells`、`star_cells`、`diamond_cells`、`triangle_cells` 和 `*_cells_by_rotation` 都使用物品本地坐标。

相对坐标可以是负数。比如一个斜向物品不需要强行找左上角，只要选一个容易理解的参考点，再把占用格写成相对这个参考点的位置。

普通物品使用 `star_cells`、`diamond_cells`、`triangle_cells`，这些 marker 会按 `rotation` 旋转。特殊物品使用 `*_cells_by_rotation`，`place_item` 直接读取对应旋转状态的 marker，不再对这些 marker 调用 `rotate_cells`。

`Bag of Stones` 和药水类物品不能作为普通星位旋转样例。wiki.gg 页面说明它们的星位始终在物品垂直上方，不遵循普通旋转变换，所以这里直接写出四种旋转状态下的 `star_cells_by_rotation`。

来源备注：`Bag of Stones` 页面修订时间 `2025-09-19T04:52:07Z`，`Potion` 页面修订时间 `2024-03-20T09:28:17Z`，`Health Potion` 页面修订时间 `2025-09-19T03:30:04Z`；查询日期 `2026-07-07`。

`Mage Hat` 使用 star、diamond 和 triangle 三类 marker。wiki.gg `Template:Grid` 中 `2` 表示 Star、`3` 表示 Diamond、`4` 表示 tertiary 图标；`Mage Hat` 页面效果文本将 `4` 作为 triangle 使用。`Mage Hat` 页面修订时间 `2025-10-17T17:30:53Z`，`Template:Grid` 修订时间 `2025-10-29T09:33:11Z`；查询日期 `2026-07-07`。

## 旋转规则

`rotate_cells(cells, rotation)` 只负责把相对于参考点的坐标按角度旋转：

```text
0:   ( x,  y)
90:  (-y,  x)
180: (-x, -y)
270: ( y, -x)
```

V1 中正向旋转按 `x` 向右、`y` 向上的坐标系逆时针计算。

`place_item(item_spec, placement)` 负责把旋转结果平移到全局坐标。

平移规则：

1. 先旋转 `shape_cells`。
2. 对每类 marker，如果物品定义了 `*_cells_by_rotation`，直接读取当前 `placement.rotation` 对应的坐标。
3. 对每类 marker，如果物品没有定义 `*_cells_by_rotation`，就旋转对应的 `*_cells`。
4. 每个旋转后的占用格和当前旋转状态的 marker，都直接加上 `placement.x` 和 `placement.y`，得到全局坐标。

这样 `placement.x` 和 `placement.y` 始终表示物品参考点的全局坐标。

## 构建结果

构建后的背包只包含三类信息：

```python
built_backpack = {
    "items": placed_items,
    "occupancy_matrix": occupancy_matrix,
    "marker_links": marker_links,
}
```

### items

每个放入背包的物品实例按输入列表顺序生成 `item_key`。
`item_key` 按同名 `item_id` 的出现次数生成，例如 `stone1`、`stone2`、`banana1`。

```python
placed_item = {
    "item_key": "stone1",
    "item_id": "stone",
    "x": 0,
    "y": 0,
    "rotation": 0,
    "occupied_cells": [(0, 0)],
    "star_cells": [],
    "diamond_cells": [],
    "triangle_cells": [],
}
```

`item_key` 用来区分同名物品实例，并作为后续战斗模块的实例身份。

这里的 `x` 和 `y` 是参考点坐标，不表示物品外框左上角。

### occupancy_matrix

占用矩阵大小固定为 `7` 行、`9` 列。

```python
occupancy_matrix = [
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    ["stone1", None, None, None, None, None, None, None, None],
]
```

矩阵规则：

- 空格是 `None`。
- 被占用格是 `item_key`。
- 矩阵第 0 行显示背包顶部，第 6 行显示背包底部。
- 矩阵列下标对应 `x`。
- 如果用 Python 的 0-based 行下标访问矩阵，行下标是 `6 - y`。
- 也就是用 `occupancy_matrix[6 - y][x]` 访问坐标 `(x, y)` 对应的格子。

### marker_links

如果一个物品的 marker 落在另一个物品占用格上，就生成一条关联：

```python
marker_link = {
    "source_item_key": "source1",
    "target_item_key": "target1",
    "star_cell": (1, 0),
}
```

字段含义：

- `source_item_key`：拥有这个 marker 的物品实例。
- `target_item_key`：被这个 marker 指到的物品实例。
- `star_cell` / `diamond_cell` / `triangle_cell`：marker 所在的全局坐标。

## 最小函数

V1 只实现以下四个函数，不额外增加功能函数。

### rotate_cells(cells, rotation)

输入相对坐标列表和旋转角度，返回旋转后的相对坐标列表。

只处理坐标变换，不做越界检查，不访问背包矩阵。

### place_item(item_spec, placement)

输入物品定义和放置参数，返回单个 `placed_item`。

负责：

- 旋转占用格。
- 普通物品旋转 `star_cells`、`diamond_cells`、`triangle_cells`。
- 特殊物品直接读取对应的 `*_cells_by_rotation[rotation]`。
- 按参考点平移。
- 生成全局 `occupied_cells`。
- 生成全局 `star_cells`、`diamond_cells`、`triangle_cells`。

### build_occupancy_matrix(placements, item_catalog)

输入放置列表和物品定义，返回 `occupancy_matrix` 和 `placed_items`。

负责：

- 检查 `item_id` 是否存在。
- 检查 `rotation` 是否合法。
- 调用 `place_item`，让普通星位和特殊星位规则都进入 `placed_items`。
- 检查占用格是否在 9x7 范围内。
- 检查占用格是否和已有物品重叠。
- 按同名出现次数生成 `item_key`。
- 把 `item_key` 写入矩阵。

### find_marker_links(placed_items, occupancy_matrix, marker_type)

输入已放置物品、占用矩阵和 marker 类型，返回对应 marker links。

规则：

- marker 落在另一个物品占用格上，生成关联。
- marker 落空，不生成关联。
- marker 越界，不生成关联。
- marker 指向自己，不生成关联。

`find_star_links`、`find_diamond_links`、`find_triangle_links` 是针对三类 marker 的薄封装。

## 校验规则

V1 只做以下校验：

- `item_id` 不存在时报错。
- `rotation` 不是 `0`、`90`、`180`、`270` 时报错。
- 物品定义了 `*_cells_by_rotation` 但没有穷举四种合法旋转状态时报错。
- 物品占用格超出 9x7 矩阵时报错。
- 两个物品占用同一格时报错。

V1 不把以下情况当作错误：

- 星位落空。
- 星位越界。
- 星位指向自己。

这些情况只是不生成 `star_link`。

## 验收场景

实现时至少覆盖以下场景：

- 单个 1x1 物品能正确写入 9x7 矩阵。
- 两个物品不重叠时矩阵正确。
- 重叠放置失败。
- 越界放置失败。
- L 形物品旋转后占用格正确。
- 参考点不在 `shape_cells` 中时，物品仍能正确写入矩阵。
- 普通物品的 marker cells 会跟随 `rotation` 旋转。
- 特殊物品的 `*_cells_by_rotation` 会按当前 `rotation` 直接读取，不再额外旋转。
- star、diamond、triangle 指向另一个物品时生成对应 link。
- marker 落空时不生成 link。
- marker 越界时不生成 link。
- marker 指向自己时不生成 link。

## 暂不实现

V1 明确不实现：

- 商店。
- 背包格或袋子解锁。
- 合成。
- 战斗效果。
- 真实物品数据导入。
- UI。
- 强化学习环境接口。
