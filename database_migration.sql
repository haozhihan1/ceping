-- 数据库迁移文件
-- 生成时间: 2025-10-17 10:55:24
-- 此文件包含完整的数据库结构和数据

-- 表: questions
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    题目 TEXT NOT NULL,
    选项 TEXT NOT NULL,
    题目类型 TEXT NOT NULL,
    正确答案 TEXT
);

-- 插入 questions 表数据
INSERT INTO questions VALUES (1, '你发现公司市场策略已不再有效，但上级暂未意识到。你会：', 'A=按现有方向执行，避免冲突;B=收集数据和案例，提出调整建议;C=私下与同级沟通，看谁先提;D=继续执行，等待上级指令', '情境题', 'B');
INSERT INTO questions VALUES (2, '双向选择：A=我更注重遵循组织的既定目标 B=我更关注未来趋势并主动调整策略', 'A=我更注重遵循组织的既定目标;B=我更关注未来趋势并主动调整策略', '双向选择题', NULL);
INSERT INTO questions VALUES (3, '我通常避免参与涉及高风险或不确定性的决策。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (4, '当项目进展缓慢但团队仍信心满满时，我会：', 'A=保持乐观，不打击士气;B=分析瓶颈，调整方向并沟通原因;C=等待更多数据后再决策;D=责备进展慢的责任人', '情境题', 'B');
INSERT INTO questions VALUES (5, '如果一项决策与我个人观点相悖，我倾向于被动执行而不提出异议。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (6, '一名表现良好的员工近两月绩效下滑，你会：', 'A=直接提醒其调整状态;B=约谈了解其困难并提供支持;C=先观察是否短期波动;D=调整任务，分配给他人', '情境题', 'B');
INSERT INTO questions VALUES (7, '我通常会回避与表现不佳的员工的直接沟通。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (8, '双向选择：A=我更擅长制定标准与规则 B=我更擅长激发团队主动性', 'A=我更擅长制定标准与规则;B=我更擅长激发团队主动性', '双向选择题', NULL);
INSERT INTO questions VALUES (9, '团队中两名骨干因资源冲突争执升级，你会：', 'A=要求立即各自反省;B=请双方冷静后召开三方沟通;C=让各自主管协调解决;D=视为个别事件，不干预', '情境题', 'B');
INSERT INTO questions VALUES (10, '我认为优秀的管理者不应过多干涉下属的工作细节。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (11, '你在会议上提出的方案被高管质疑，你会：', 'A=坚持己见并辩论到底;B=解释逻辑并邀请共同探讨;C=暂时沉默，事后沟通;D=当场认同并撤回意见', '情境题', 'B');
INSERT INTO questions VALUES (12, '面对不同意见时，我通常选择避免争论，以免引发不快。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (13, '双向选择：A=我倾向于用事实与逻辑说服他人 B=我倾向于用情感与共识影响他人', 'A=我倾向于用事实与逻辑说服他人;B=我倾向于用情感与共识影响他人', '双向选择题', NULL);
INSERT INTO questions VALUES (14, '某跨部门项目出现信息误传，导致延误。你会：', 'A=公开说明原因，建立统一沟通机制;B=仅在内部总结经验教训;C=找责任方说明问题即可;D=向上级汇报以免被误解', '情境题', 'A');
INSERT INTO questions VALUES (15, '我认为部门间沟通问题主要是对方不配合所致。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (16, '临近项目截止日期，进度落后30%。你会：', 'A=立即加班追赶，确保交付;B=分析关键环节，重组计划;C=上报领导寻求延期;D=压缩验收环节确保交差', '情境题', 'B');
INSERT INTO questions VALUES (17, '只要上级未催，我通常不会主动更新项目进展。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (18, '双向选择：A=我更关注按流程规范推进任务 B=我更关注灵活调整以保证结果', 'A=我更关注按流程规范推进任务;B=我更关注灵活调整以保证结果', '双向选择题', NULL);
INSERT INTO questions VALUES (19, '当发现项目中有轻微违规操作但能加快进度时：', 'A=严格纠正;B=先警告并设限;C=暂时接受以免拖延;D=视情况处理', '情境题', 'A');
INSERT INTO questions VALUES (20, '在面对多任务时，我常常无法有效区分优先级。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (21, '上级安排你负责一个你不熟悉的新业务领域，你会：', 'A=先收集资料，自行摸索;B=主动请教专家并快速组建团队;C=观察他人做法后再行动;D=拒绝或拖延', '情境题', 'B');
INSERT INTO questions VALUES (22, '我很少会复盘失败的项目或错误。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (23, '双向选择：A=我更愿意不断尝试新方法，即使风险高 B=我更倾向于使用经过验证的方法', 'A=我更愿意不断尝试新方法，即使风险高;B=我更倾向于使用经过验证的方法', '双向选择题', NULL);
INSERT INTO questions VALUES (24, '你提出的新方案未被采纳，后来事实证明原方案失败。你会：', 'A=事后强调自己的判断;B=总结原因并在下次改进提案方式;C=不再提出新想法;D=与领导私下沟通复盘', '情境题', 'B');
INSERT INTO questions VALUES (25, '我认为创新更多是领导层的责任，而非普通管理者。', '1=非常不符合，2=不太符合，3=一般，4=较符合，5=非常符合', '反向题', NULL);
INSERT INTO questions VALUES (26, '常阅读跨领域前沿文章', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (27, '改变生活习惯会感到不适', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (28, '享受解决复杂问题的过程', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (29, '严格按计划执行工作', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (30, '截止日前常需加班赶工', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (31, '坚持每日复盘工作得失', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (32, '大型社交场合能快速连接', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (33, '独处比聚会更让我放松', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (34, '擅长即兴演讲调动气氛', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (35, '即使对方无理也先理解情绪', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (36, '为达目标可暂时牺牲关系', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (37, '主动调解同事间矛盾', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (38, '突发危机时思维更清晰', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (39, '未读消息堆积引发焦虑', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (40, '重大失误后立即投入补救', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (41, '他人负面评价让我纠结', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (42, '喜欢重构现有工作流程', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (43, '文件归档总是清晰规范', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (44, '认为职场友善是专业素养', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (45, '压力下仍能保持耐心', '1=非常不准，2=不太准，3=一般，4=较准，5=非常准确', '评分', NULL);
INSERT INTO questions VALUES (46, '在紧急情况下，我倾向于迅速做出决定而不拖延', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (47, '当面临选择时，我通常很快就能确定最佳方案', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (48, '我经常设定明确的时间表来完成任务', '1=从不，2=很少，3=有时，4=经常，5=总是', '评分', NULL);
INSERT INTO questions VALUES (49, '面对截止日期，我会感到压力并加快工作节奏', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (50, '在团队中，我通常承担领导角色，推动项目进展', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (51, '在会议中，我经常主动发言表达观点', '1=从不，2=很少，3=有时，4=经常，5=总是', '评分', NULL);
INSERT INTO questions VALUES (52, '我喜欢在团队中分享我的想法和经历', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (53, '我的情绪变化通常比较明显，容易被他人察觉', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (54, '我倾向于用夸张的手势和表情来表达自己', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (55, '我经常成为团队中的气氛活跃者', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (56, '我更喜欢按照既定流程工作，避免频繁变化', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (57, '突然的变动会让我感到不安，需要时间适应', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (58, '我会主动帮助团队成员解决问题', '1=从不，2=很少，3=有时，4=经常，5=总是', '评分', NULL);
INSERT INTO questions VALUES (59, '我重视与同事之间的和谐关系', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (60, '我倾向于支持同事，维持团队和谐', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (61, '我严格遵守公司的规章制度，不轻易违反', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (62, '我在工作中注重细节，追求完美', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (63, '在做决策时，我会优先考虑可能的风险和负面影响', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (64, '我倾向于选择稳妥的方案，即使收益可能较低', '1=完全不符合，2=不符合，3=一般，4=符合，5=非常符合', '评分', NULL);
INSERT INTO questions VALUES (65, '我会反复检查工作成果，确保没有错误', '1=从不，2=很少，3=有时，4=经常，5=总是', '评分', NULL);
INSERT INTO questions VALUES (66, '高屋建瓴形容视野开阔、谋划远大；高瞻远瞩指目光远大、谋划长远。两成语的关系是：', 'A) 近义词;B) 反义词;C) 包含关系;D) 交叉关系', '单选', 'A');
INSERT INTO questions VALUES (67, '面对激烈的市场竞争，企业唯有创新才能突围，行业呈现出____的态势。最恰当的成语是：', 'A) 如火如荼;B) 胶着激烈;C) 风起云涌;D) 此消彼长', '单选', 'C');
INSERT INTO questions VALUES (68, '辩论：甲说''所有成功企业都投广告，因此只要投广告就能成功''；乙反驳''某企业没投广告也成功，所以广告无用''。逻辑漏洞主要存在于：', 'A) 仅甲方（混淆充分必要条件）;B) 仅乙方（以偏概全）;C) 双方都有;D) 都没有', '单选', 'C');
INSERT INTO questions VALUES (69, '将下列句子排成通顺段落：①市场竞争白热化 ②唯有创新突围 ③企业需聚焦用户 ④持续迭代产品。最合理的顺序是：', 'A) ①→③→④→②;B) ①→②→③→④;C) ②→③→①→④;D) ③→①→②→④', '单选', 'A');
INSERT INTO questions VALUES (70, '句子：''市场是一只看不见的手，悄悄塑造了行业格局''。所用修辞手法：', 'A) 明喻（明确使用比喻词）;B) 暗喻（隐含比喻）;C) 拟人（赋予人类特征）;D) 夸张（夸大描述）', '单选', 'B');
INSERT INTO questions VALUES (71, '报道A称''行业并购将提升运营效率''，报道B称''大规模并购会导致市场垄断''。两篇报道的核心立场：', 'A) 相同（都支持并购）;B) 对立（效率vs垄断）;C) 部分相同;D) 无法判断', '单选', 'B');
INSERT INTO questions VALUES (72, '以下哪句可作为《AI边缘计算部署》技术白皮书的通俗摘要？', 'A) ''将AI模型部署到终端设备，实现本地实时处理'';B) ''边缘计算=云计算简化版'';C) ''边缘部署就是远程控制设备'';D) ''边缘计算只是概念炒作''', '单选', 'A');
INSERT INTO questions VALUES (73, '原邮件：''请尽快把资料发我，谢谢！''。以下修改最能体现专业度的是：', 'A) ''请于24小时内提交所需资料，感谢配合！'';B) ''立刻发给我！'';C) ''资料，急用！'';D) ''有空时请处理''', '单选', 'A');
INSERT INTO questions VALUES (74, '《出师表》：''亲贤臣，远小人，此先汉所以兴隆也''。作者诸葛亮的核心观点是：', 'A) 重用贤臣是兴国之本;B) 远离小人即可治国;C) 东汉因亲贤而衰亡;D) 自我推荐为贤臣', '单选', 'A');
INSERT INTO questions VALUES (75, '劳动合同条款：''员工加班需经书面批准，否则视为自愿加班不支付报酬''。该条款的关键限制是：', 'A) 加班必须预先审批;B) 未批准即视为自愿;C) 设定了加班费上限;D) 实际无实质约束', '单选', 'A');
INSERT INTO questions VALUES (76, '向市场部同事解释''API接口''，最恰当的比喻是：', 'A) ''像电源插座，实现不同系统间的数据互通'';B) ''专业编程术语，不需要理解'';C) ''类似电脑USB接口'';D) ''无实际价值的IT概念''', '单选', 'A');
INSERT INTO questions VALUES (77, '为''碳足迹追踪''环保APP设计标语，最具吸引力的是：', 'A) ''绿色出行，每一步守护地球！'';B) ''出行必备工具'';C) ''环保从今天开始'';D) ''强制环保，从我做起''', '单选', 'A');
INSERT INTO questions VALUES (78, '杜甫诗句：''风急天高猿啸哀，渚清沙白鸟飞回''。整体情感基调是：', 'A) 积极昂扬;B) 凄凉萧瑟;C) 平静中立;D) 悲喜交加', '单选', 'B');
INSERT INTO questions VALUES (79, '议论文首段提出''远程办公显著提升工作效率''后，接下来最合理的论证方向是：', 'A) 分析降低通勤时间的效益;B) 讨论增加的管理成本;C) 批判导致失业风险;D) 强调技术依赖问题', '单选', 'A');
INSERT INTO questions VALUES (80, '商业分析报告：''数据驱动型企业增速超行业均值130%，但忽视安全的企业事故率增长400%。技术只是放大器，人才是决策核心''。作者核心观点是：', 'A) 数据驱动决定商业未来;B) 数据安全高于一切;C) 技术是工具，人才是关键;D) 人类不会被AI取代', '单选', 'C');
INSERT INTO questions VALUES (81, '某产品原价100元，降价20%后销量增长30%。总收入变化：', 'A) 增长4%;B) 下降4%;C) 增长8%;D) 下降8%', '单选', 'A');
INSERT INTO questions VALUES (82, '季度销售额（万元）：1月100，2月105，3月110，4月115。该季度复合增长率：', 'A) 1.6%;B) 3.2%;C) 4.8%;D) 6.4%', '单选', 'B');
INSERT INTO questions VALUES (83, '抛硬币3次，至少出现2次正面的概率：', 'A) 12.5%;B) 37.5%;C) 50%;D) 62.5%', '单选', 'B');
INSERT INTO questions VALUES (84, '项目总收益18万元，总成本15万元。投资回报率(ROI)：', 'A) 16.7%;B) 20%;C) 25%;D) 30%', '单选', 'B');
INSERT INTO questions VALUES (85, '解方程组：2x + 3y = 16；3x - y = 5。正确解为：', 'A) x=3,y=3;B) x=4,y=2;C) x=2,y=4;D) x=5,y=1', '单选', 'B');
INSERT INTO questions VALUES (86, '某物流网络5个节点距离矩阵(km)：A→B:3, A→C:5, B→D:4, C→D:2, D→E:6。A到E的最短路径：', 'A) A→B→D→E(13km);B) A→C→D→E(13km);C) A→B→C→E(14km);D) A→C→B→E(15km)', '单选', 'A');
INSERT INTO questions VALUES (87, '产品组装工序：设计(2h)→采购(3h)→生产(4h)→质检(1h)。在平行作业时的最短完工时间：', 'A) 10小时（顺序进行）;B) 7小时（设计采购并行）;C) 6小时（全流程优化）;D) 5小时（增加人力）', '单选', 'B');
INSERT INTO questions VALUES (88, '投资组合：股票(预期收益12%)占比60%，债券(预期收益5%)占比40%。组合预期收益：', 'A) 7.2%;B) 8.8%;C) 9.5%;D) 10.2%', '单选', 'B');
INSERT INTO questions VALUES (89, '产品固定成本10万元，单价500元，单位变动成本300元。盈亏平衡点销量：', 'A) 200件;B) 300件;C) 400件;D) 500件', '单选', 'B');
INSERT INTO questions VALUES (90, '近6个月销售数据线性回归斜率=+1.5（万元/月）。下月趋势预测：', 'A) 稳步上升;B) 小幅下降;C) 维持平稳;D) 剧烈波动', '单选', 'A');
INSERT INTO questions VALUES (91, '汇率变动：美元/人民币7.0→7.2，欧元/美元1.1→1.05。用1000美元套利的策略：', 'A) 美元→人民币→欧元→美元;B) 美元→欧元→人民币→美元;C) 持有美元不动;D) 买入黄金对冲', '单选', 'A');
INSERT INTO questions VALUES (92, '年销售商品1800件，平均库存300件。年库存周转率：', 'A) 4次;B) 6次;C) 8次;D) 12次', '单选', 'B');
INSERT INTO questions VALUES (93, '投资项目：70%概率获利3万，30%概率亏损1万。期望收益：', 'A) 1.8万元;B) 2.1万元;C) 2.4万元;D) 2.7万元', '单选', 'B');
INSERT INTO questions VALUES (94, '生产数据：产量达500台时单位成本最低，超量后成本回升。这反映边际效益：', 'A) 先递增后递减;B) 持续递减;C) 保持恒定;D) 不规则波动', '单选', 'B');
INSERT INTO questions VALUES (95, '库存模型：订货成本200元/次，持有成本5元/件/月，缺货损失10元/件。最优订货量取决于：', 'A) EOQ经济订货模型;B) ABC分类法;C) JIT零库存;D) 安全库存模型', '单选', 'A');
INSERT INTO questions VALUES (96, '图形序列：○●○●○●__。下一个图形：', 'A) ●;B) ○;C) ●●;D) ○○', '单选', 'A');
INSERT INTO questions VALUES (97, '前提：所有管理者都需要领导力；有些技术专家具有领导力。可推出的结论：', 'A) 所有技术专家都是管理者;B) 有些管理者是技术专家;C) 领导力只存在于管理者;D) 无法确定关系', '单选', 'B');
INSERT INTO questions VALUES (98, '九宫格数字规律：第一行[2,7,6]，第二行[9,5,1]，第三行[4,3,?]。缺失值：', 'A) 8;B) 10;C) 12;D) 0', '单选', 'D');
INSERT INTO questions VALUES (99, '案件线索：①金库密码锁完好②监控显示单人作案③财务总监称案发时在出差④保险柜仅指纹解锁。矛盾点：', 'A) ①与②;B) ②与③;C) ③与④;D) ①与④', '单选', 'C');
INSERT INTO questions VALUES (100, '研发流程：①需求分析→②原型设计→③__→④测试发布。缺失环节：', 'A) 技术评审;B) 市场调研;C) 代码开发;D) 用户培训', '单选', 'C');
INSERT INTO questions VALUES (101, '语句：''本语句是假的''。这属于：', 'A) 典型的语义悖论;B) 合理陈述;C) 语法错误;D) 比喻修辞', '单选', 'A');
INSERT INTO questions VALUES (102, '类比：钢笔用于书写，如同刀具用于：', 'A) 切割;B) 奔跑;C) 阅读;D) 遮蔽', '单选', 'A');
INSERT INTO questions VALUES (103, '验证''员工培训→生产率提升''的因果关系，最可靠方法：', 'A) 实验组对照组对比;B) 历史数据回归;C) 员工满意度调查;D) 个案深度访谈', '单选', 'A');
INSERT INTO questions VALUES (104, '数列：3, 6, 12, 24, 48, ?。下一个数：', 'A) 72;B) 84;C) 96;D) 108', '单选', 'C');
INSERT INTO questions VALUES (105, '广告语：''不用我们的产品就是不支持国货''。逻辑谬误类型：', 'A) 道德绑架;B) 滑坡谬误;C) 虚假两难;D) 合理推论', '单选', 'A');
INSERT INTO questions VALUES (106, '投资选择：方案A稳定收益8%，方案B高风险收益15%。风险厌恶者应选：', 'A) 方案A;B) 方案B;C) 各投50%;D) 暂不投资', '单选', 'A');
INSERT INTO questions VALUES (107, '公司中：所有经理都是全职员工，部分技术专家是兼职。两集合关系：', 'A) 经理包含专家;B) 存在交叉（有全职专家）;C) 互斥关系;D) 完全相同', '单选', 'B');
INSERT INTO questions VALUES (108, '三人陈述：甲说''乙说真话''；乙说''丙说谎''；丙说''两人都说谎''。实际说谎者：', 'A) 只有甲;B) 只有乙;C) 只有丙;D) 甲和乙', '单选', 'C');
INSERT INTO questions VALUES (109, '项目管理流程：①计划制定→②__→③绩效评估→④经验复盘。正确顺序：', 'A) ①②③④;B) ①④②③;C) ②①③④;D) ③①②④', '单选', 'A');
INSERT INTO questions VALUES (110, '仓库尺寸10×8m，货架规格2×1m。最大存储量方案：', 'A) 40个（5行8列）;B) 36个（6行6列）;C) 32个（4行8列）;D) 28个（7行4列）', '单选', 'A');
INSERT INTO questions VALUES (111, '立方体展开图：底面标记★，前面标记●。折叠后●在★的：', 'A) 正前方;B) 正上方;C) 正右方;D) 正后方', '单选', 'B');
INSERT INTO questions VALUES (112, '机械零件三视图中，主视图显示圆孔，俯视图显示方槽。立体结构是：', 'A) 圆柱体带方槽;B) 立方体带圆孔;C) 圆锥体;D) 球体', '单选', 'A');
INSERT INTO questions VALUES (113, '迷宫地图：起点→岔路(左死路/右通道)→环形区→终点。最短路径：', 'A) 直行穿越环形区;B) 右转绕行;C) 左转后退;D) 环形区迂回', '单选', 'B');
INSERT INTO questions VALUES (114, '正方形纸对折两次后切角展开。展开图形状：', 'A) 中心方孔;B) 四角星形;C) 十字对称;D) 放射条纹', '单选', 'C');
INSERT INTO questions VALUES (115, '建筑平面图：圆形大厅+放射走廊。立体化后是：', 'A) 穹顶式会堂;B) 方形办公楼;C) 阶梯教室;D) 长廊展厅', '单选', 'A');
INSERT INTO questions VALUES (116, '零件装配顺序：基座→轴承→齿轮→外壳。必要约束是：', 'A) 轴承需在齿轮前安装;B) 外壳需最先安装;C) 齿轮可最后安装;D) 无固定顺序', '单选', 'A');
INSERT INTO questions VALUES (117, '立方体在左上光源下的阴影方向：', 'A) 右下延伸;B) 左下延伸;C) 正下投影;D) 无阴影', '单选', 'A');
INSERT INTO questions VALUES (118, '下列图形中具有180°旋转对称性的是：', 'A) 矩形;B) 直角三角形;C) 梯形;D) 平行四边形', '单选', 'A');
INSERT INTO questions VALUES (119, '二维草图：正视图圆形+侧视图矩形。对应三维物体：', 'A) 圆柱体;B) 球体;C) 立方体;D) 圆锥体', '单选', 'A');
INSERT INTO questions VALUES (120, '地图比例尺1:5000，图上距离4cm。实际距离：', 'A) 200米;B) 300米;C) 400米;D) 500米', '单选', 'A');
INSERT INTO questions VALUES (121, '杠杆平衡：支点左侧40cm处2kg，右侧需在60cm处放置：', 'A) 1kg;B) 1.5kg;C) 2kg;D) 3kg', '单选', 'B');
INSERT INTO questions VALUES (122, '图形拓扑关系：咖啡杯与甜甜圈属于：', 'A) 拓扑等价（单孔结构）;B) 完全不同;C) 局部相似;D) 无法比较', '单选', 'A');
INSERT INTO questions VALUES (123, '物体三视图：主视三角形+俯视圆形+侧视矩形。该物体是：', 'A) 圆锥体;B) 三棱柱;C) 圆柱体;D) 球体', '单选', 'A');
INSERT INTO questions VALUES (124, '空间记忆测试：会议室布局（门→桌→柜→窗）。正确还原：', 'A) 门-桌-柜-窗;B) 窗-柜-桌-门;C) 门-窗-桌-柜;D) 柜-门-窗-桌', '单选', 'A');
INSERT INTO questions VALUES (125, '立方体在左上光源下的阴影方向：', 'A) 右下延伸;B) 左下延伸;C) 正下投影;D) 无阴影', '单选', 'A');

-- 索引: idx_questions_id
CREATE INDEX idx_questions_id ON questions(id);

-- 表: employees
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY,
    姓名 TEXT NOT NULL,
    工号 TEXT NOT NULL,
    公司名称 TEXT,
    管理能力 INTEGER DEFAULT 0,
    战略思维 INTEGER DEFAULT 0,
    团队领导 INTEGER DEFAULT 0,
    执行管控 INTEGER DEFAULT 0,
    跨部门协作 INTEGER DEFAULT 0,
    外向性 INTEGER DEFAULT 0,
    宜人性 INTEGER DEFAULT 0,
    开放性 INTEGER DEFAULT 0,
    责任心 INTEGER DEFAULT 0,
    行为模式类型 TEXT,
    行为模式分数 INTEGER DEFAULT 0,
    性格特质类型 TEXT,
    性格特质分数 INTEGER DEFAULT 0,
    通用能力 INTEGER DEFAULT 0,
    言语理解 INTEGER DEFAULT 0,
    数量分析 INTEGER DEFAULT 0,
    逻辑推理 INTEGER DEFAULT 0,
    空间认知 INTEGER DEFAULT 0,
    创建时间 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入 employees 表数据
INSERT INTO employees VALUES (1, '雪', '12312312345', 'wanji', 1.96, 1.8, 1.6, 2.2, 1.8, 5, 5, 5, 5, 'D型支配型/I型影响型', 5, '外向性/宜人性', 5, 1.67, 0, 0, 6.67, 0, '2025-10-16 01:44:53');
INSERT INTO employees VALUES (2, '张三', 'bp12138', 'bopei', 2, 2, 1.6, 2.2, 1.8, 5, 5, 5, 5, 'D型支配型/I型影响型', 5, '外向性/宜人性', 5, 1.07, 1, 1, 1.27, 1, '2025-10-16 03:22:50');

-- 索引: idx_employees_gonghao
CREATE INDEX idx_employees_gonghao ON employees(工号);

-- 表: admins
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL
);

-- 插入 admins 表数据
INSERT INTO admins VALUES (1, 'admin', 'admin123');

