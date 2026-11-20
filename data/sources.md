# 来源清单与核验说明

> 整理日期：2026-11-20。检索类信息会过期，规则以京东帮助中心当日页面为准。

## 一、产品信息（英冠 4.0 有机纯牛奶）

| 信息 | 来源 | 可靠度 | 说明 |
|---|---|---|---|
| 品名、200mL×12 盒、4.0 有机、北纬 42°、有机认证标识 | 京东商品页 https://item.jd.com/10233138053185.html | 高 | 商品标题与主图信息 |
| 4.0g 蛋白/100mL、135mg 钙/100mL、配料仅生牛乳 | 京东商品页 + 品牌短视频 https://www.iesdouyin.com/share/video/7656622795090962043 | 中高 | 品牌自述口径，建议以实物包装营养成分表复核 |
| “限定产自北纬 42° 黄金牧场”“有机认证” | 品牌短视频 https://www.iesdouyin.com/share/video/7679349113934609905 | 中 | 营销口径，认证编号需看包装 |
| 保质期 6 个月、生产工厂、生产许可证 | **未核到官方页面** | 低 | 仅按同类常温灭菌乳推断；必须看盒身标注 |
| 品牌背景、400 电话 | 行业分析文 http://m.toutiao.com/group/7706734676303446571/ | 低 | 自媒体内容，不作为对外承诺依据 |

## 二、京东平台规则（官方帮助中心）

| 规则 | 链接 |
|---|---|
| 7 天无理由退货规则说明（第三方） | https://help.jd.com/user/issue/289-3781.html |
| 京东自营商品售后政策服务总则（7 退 15 换、完好判定） | https://help.jd.com/user/issue/327-988.html |
| 第三方商家售后规则（生鲜 48 小时、不适用无理由清单） | https://help.jd.com/user/issue/329-4274.html |
| 效期无忧（剩余保质期要求） | https://help.jd.com/user/issue/942-3992.html |
| 价格保护服务（含 7 天周期、申请路径、不支持场景） | https://help.jd.com/user/issue/291-4537.html |
| 价格保护（自营商品，7 天类目清单） | https://ihelp.jd.com/n/help/tip/getTipsFacade.json?tipId=174 |
| 晚发赔（6 元 / 20 元档位、48 小时考核） | https://helpcenter.jd.com/vender/issue/1000-44103.html |
| 破损包退换保险（食品生鲜 48 小时、凭证要求） | https://help.jd.com/user/issue/942-4438.html |
| 免费上门退换（第三方，7 天退 / 15 天换、理赔次数） | https://help.jd.com/user/issue/129-4298.html |
| 免费上门退换（厂商直送，理赔时效） | https://help.jd.com/user/issue/321-4436.html |
| 售后审核时效（第三方 48 小时） | https://help.jd.com/issue/search?siteId=5&keyword=48 （帮助中心搜索页，条目会变动） |

## 三、营养与标准

| 依据 | 来源 | 说明 |
|---|---|---|
| 灭菌乳蛋白质 ≥2.9g/100g（GB 25190-2010） | 民福康科普 https://mip.mfk.com/jingbian/6qqb8aksyb3.shtml | 二手引用，标准号可查证 |
| 成人每日奶类 300～500g | 国家卫健委在线访谈 https://www.nhc.gov.cn/wjw/zxft/hdjl_zxft_detail.shtml?id=446ec2ddcce84898b92598c68cf86ddb | 权威 |
| 常温奶 UHT 135℃、开封后冷藏 24 小时 | 丁香医生 http://m.toutiao.com/group/6902624820366672391/ | 科普媒体，与包装说明一致 |
| 加热方式、煮沸损失、1 岁内不喝纯牛奶 | 人民网健康 http://health.people.com.cn/n1/2016/0819/c21471-28648886.html ；儿科科普 http://m.toutiao.com/group/7626971248467116544/ | 与膳食指南一致 |
| 高蛋白实现方式（牛种/饲料/膜过滤） | 科普中国 https://cloud.kepuchina.cn/h5/detail?id=7486517190718656512 | 科普 |
| 煮沸对营养影响有限 | 科普中国辟谣 https://piyao.kepuchina.cn/rumor/rumordetail?id=JMgY | 用于平衡“别煮沸”的口径 |
| 1 岁后引入全脂纯牛奶、每日奶量 | 育儿科普 http://m.toutiao.com/group/7698740746458907164/ | 二手，与指南一致 |

## 四、待核验清单（上线前必须补齐）

1. 盒身保质期天数、生产工厂名称与地址、SC 生产许可证编号。
2. 当前在售 SKU 与箱规（是否有 10 盒/16 盒/24 盒、单盒装）。
3. 商品页售后标识：是否“7 天无理由”“坏损包退”“效期无忧”“免费上门退换”“晚发赔”。
4. 真实客服历史会话（用于补充话术与 badcase，比任何科普都重要）。
5. 仓库发货地与承运商，用于回答“几天到”。

> 使用方法：`verified=low/medium` 的条目，在 RAG 提示词里要求模型加“以商品页/包装为准”，不要当成硬事实输出。

> （注：部分内容由豆包 AI 生成）