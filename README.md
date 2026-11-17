# 非遗联名商品页面的授权展示核验

这是非遗联名资料的本地演练门户与目录采集器。演练数据仅在环回地址提供，不会操作真实用户、订单或商户。`app.capture.read_catalog` 读取目录；`app.capture.observe_detail` 走卡片到详情，在一次页面会话内记录规格选择、图片轮播与授权详情，每条采集记录带来源地址、规格、素材版本与采集时刻，不同规格或不同发布时刻的素材各自成行、不拼成一款商品；`app.records.save_observations` 追加式保存采集记录；`app.review.review_observations` 面向业务汇总缺口与原始页面出处——轮播懒加载失败、授权撤回、授权链接指向非授权站点都记为缺口，图像缺失只记素材缺口，不视为商品下架。

站点约定见 `docs/portal.md`；测试时从本地任意空闲端口启动演练站点。安装锁定依赖并准备 Chromium 后：

- `python -m unittest discover -s tests -v`：运行基线浏览器测试。
- `python -m compileall -q app tests`：检查代码。
- `python -m app.site`：启动本地演练站点。
- `python -m app.cli`：另一个终端观察目录输出，并对每个商品做一次详情采集，记录写入 `var/observations.sqlite3` 后打印业务汇总；`python -m app.cli ip-03 典藏款` 可对指定商品与规格单独采集。

两个终端命令用于人工演示，自动测试不依赖固定端口。
