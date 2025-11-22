
本需求提到的所有程序和数据的入口都在tool目录下

请阅读 ui_for_pic.py 模块，其目的在于第一次去寻找和截图，构建workflow图库。

结果在picture目录下，从两个txt可以看出，已经生成了很多workflow信息，并将其命名（png文件名） 并在name_map.txt中，已经记录了文件名和workflow的对应关系

同时，在not_found.txt中，记录了web端获取到的workflow和预期不一致，导致没有找到目标workflow的情况，这是因为这是一个大模型驱动的功能，所以每次运行相同输入，输出结果未必相同。

---

以上是前情需要，下面是这次的两个需求

---

需求一

按照当前的信息，构建一个完整的workflow管理方案：在picture目录下，放置截图，文件名作为每个workflow的id标识；

构建一个sqlite数据表，用于记录workflow的详细信息（id， workflow的json(目前在not_found，name_map中用于标记workflow的json字符串)， catalog， items），有一个专门的python模块，对该sqlite进行读取管理，转换成其他的格式（csv、txt等），便于在新增workflow的时候，需要筛选查询workflow的时候，能方便地处理。这个数据库模块，可以代替当前的name_map.txt

---

需求二

对于未找到的workflow，在not_found.txt中。借鉴ui_for_pic.py 实现一个workflow_update.py，把not_found.txt中没有找到的，继续运行：遍历not_found的每一行，将其json字符串作为key，在collected_result.json中，遍历其可能的items，判断是否进入预期，如果进入预期，则截图放置到对应的目录下，将信息更新到sqlite数据库下。注意，因为是增量更新，所以id和文件名要遵循规律，如果control下面已经有了control_1.json~control_13.json，那新的数据就应该冠以control_14.json。

由于可能存在不确定性，所以workflow_update.py可以配置每个item的重复执行次数，比如配置为3，那每个item会执行3次，直到找到预期的workflow。
如果依然没有找到，就生成一份新的not_found_{time}.txt。

数据库和txt就生成到tool下面，picture下面，就只安放png就行了。