export const categoryList = [
  {
    id: 1,
    name: '物业缴费',
    description: '物业费、水电公摊、账单查询、票据开具等缴费相关知识。',
    questionCount: 12,
    sortOrder: 1,
    status: '启用',
    createdAt: '2026-01-05'
  },
  {
    id: 2,
    name: '报修服务',
    description: '室内报修、公共区域维修、电梯故障、紧急抢修等服务流程。',
    questionCount: 14,
    sortOrder: 2,
    status: '启用',
    createdAt: '2026-01-05'
  },
  {
    id: 3,
    name: '停车管理',
    description: '月租车位、临停登记、车牌识别、充电桩申请等停车业务。',
    questionCount: 10,
    sortOrder: 3,
    status: '启用',
    createdAt: '2026-01-08'
  },
  {
    id: 4,
    name: '装修管理',
    description: '装修申请、施工时间、垃圾清运、施工人员进场等管理规范。',
    questionCount: 9,
    sortOrder: 4,
    status: '启用',
    createdAt: '2026-01-10'
  },
  {
    id: 5,
    name: '生活服务',
    description: '门禁卡、快递柜、活动室预约、社区便民服务等日常事项。',
    questionCount: 8,
    sortOrder: 5,
    status: '启用',
    createdAt: '2026-01-12'
  },
  {
    id: 6,
    name: '投诉建议',
    description: '服务投诉、噪音扰民、环境秩序、处理进度查询等反馈事项。',
    questionCount: 7,
    sortOrder: 6,
    status: '启用',
    createdAt: '2026-01-15'
  }
]

export const qaList = [
  {
    id: 1,
    question: '物业费可以通过哪些方式缴纳？',
    answer:
      '您可以通过物业服务中心现场缴费、社区小程序、银行代扣或线上支付入口缴纳物业费。线上缴费完成后系统会自动生成电子凭证，如需纸质票据可到服务中心申请打印。',
    category: '物业缴费',
    keywords: ['物业费', '缴费方式', '线上支付'],
    viewCount: 1280,
    askCount: 216,
    status: '已发布',
    source: '物业收费管理制度',
    updatedAt: '2026-04-10'
  },
  {
    id: 2,
    question: '物业费逾期会产生滞纳金吗？',
    answer:
      '物业费建议按缴费周期及时缴纳。是否产生滞纳金以物业服务合同和小区公告为准，如遇特殊情况可提前联系管家登记说明。',
    category: '物业缴费',
    keywords: ['逾期', '滞纳金', '合同'],
    viewCount: 940,
    askCount: 137,
    status: '已发布',
    source: '物业服务合同',
    updatedAt: '2026-03-18'
  },
  {
    id: 3,
    question: '如何查询物业缴费明细？',
    answer:
      '登录社区小程序后进入“我的账单”，可按房号、月份和费用类型查询缴费明细。若明细与实际情况不一致，请携带房产证明或租赁证明联系服务中心核对。',
    category: '物业缴费',
    keywords: ['账单', '明细', '查询'],
    viewCount: 728,
    askCount: 103,
    status: '已发布',
    source: '线上缴费操作手册',
    updatedAt: '2026-03-05'
  },
  {
    id: 4,
    question: '家中漏水应该如何报修？',
    answer:
      '发现漏水请先关闭相关水阀并保护现场，可通过小程序提交报修，上传照片并填写房号、联系人和故障位置。紧急情况请拨打物业 24 小时值班电话，维修人员会优先处理。',
    category: '报修服务',
    keywords: ['漏水', '报修', '紧急维修'],
    viewCount: 1624,
    askCount: 311,
    status: '已发布',
    source: '工程报修服务规范',
    updatedAt: '2026-04-12'
  },
  {
    id: 5,
    question: '公共区域照明损坏怎么处理？',
    answer:
      '公共区域照明损坏可在“公共报修”中选择楼栋、楼层和位置提交，也可告知楼栋管家。物业工程人员会在受理后安排巡检维修。',
    category: '报修服务',
    keywords: ['公共区域', '照明', '工程维修'],
    viewCount: 684,
    askCount: 88,
    status: '已发布',
    source: '公共设施巡检制度',
    updatedAt: '2026-02-26'
  },
  {
    id: 6,
    question: '报修后多久会有人联系？',
    answer:
      '普通报修一般在 30 分钟内完成受理并联系业主，紧急报修将优先响应。具体上门时间会结合维修类型、配件情况和业主预约时间确认。',
    category: '报修服务',
    keywords: ['响应时间', '上门', '维修'],
    viewCount: 810,
    askCount: 142,
    status: '已发布',
    source: '客户服务响应标准',
    updatedAt: '2026-03-22'
  },
  {
    id: 7,
    question: '小区停车位如何办理月租？',
    answer:
      '办理月租车位需携带身份证、行驶证和房屋证明到物业服务中心登记，也可在线提交车辆信息。审核通过后按月缴纳停车费用并录入车牌识别系统。',
    category: '停车管理',
    keywords: ['停车位', '月租', '车牌'],
    viewCount: 1510,
    askCount: 265,
    status: '已发布',
    source: '停车场管理办法',
    updatedAt: '2026-04-08'
  },
  {
    id: 8,
    question: '临时车辆如何进入小区？',
    answer:
      '临时车辆需由业主提前在访客系统中登记车牌和访问时间，或到门岗说明来访信息。门岗核验后按临停规则放行，超时可能产生临停费用。',
    category: '停车管理',
    keywords: ['临时车辆', '访客', '门岗'],
    viewCount: 1018,
    askCount: 177,
    status: '已发布',
    source: '访客车辆通行规则',
    updatedAt: '2026-03-30'
  },
  {
    id: 9,
    question: '车牌识别失败怎么办？',
    answer:
      '车牌识别失败时请联系门岗人工核验，并检查车牌是否已完成登记、是否欠费或是否存在录入错误。确认后物业可协助更新车牌信息。',
    category: '停车管理',
    keywords: ['车牌识别', '门禁', '欠费'],
    viewCount: 650,
    askCount: 91,
    status: '已发布',
    source: '车场系统运维手册',
    updatedAt: '2026-02-18'
  },
  {
    id: 10,
    question: '装修前需要办理哪些手续？',
    answer:
      '装修前需到物业服务中心提交装修申请、施工图纸、施工人员信息和业主身份证明，签署装修管理协议并缴纳相关保证金后方可进场施工。',
    category: '装修管理',
    keywords: ['装修申请', '施工图纸', '保证金'],
    viewCount: 1386,
    askCount: 244,
    status: '已发布',
    source: '装修管理协议',
    updatedAt: '2026-04-01'
  },
  {
    id: 11,
    question: '装修施工时间有什么规定？',
    answer:
      '装修施工时间通常为工作日 8:30-12:00、14:00-18:00，周末和法定节假日禁止产生噪声施工。具体时间以小区装修管理公示为准。',
    category: '装修管理',
    keywords: ['施工时间', '噪声', '节假日'],
    viewCount: 1134,
    askCount: 198,
    status: '已发布',
    source: '小区装修公示',
    updatedAt: '2026-03-19'
  },
  {
    id: 12,
    question: '装修垃圾如何清运？',
    answer:
      '装修垃圾应袋装后放置在物业指定临时堆放点，严禁堆放在楼道、电梯厅和消防通道。清运费用和时间安排可咨询物业服务中心。',
    category: '装修管理',
    keywords: ['装修垃圾', '清运', '消防通道'],
    viewCount: 779,
    askCount: 118,
    status: '已发布',
    source: '装修垃圾清运指引',
    updatedAt: '2026-03-11'
  },
  {
    id: 13,
    question: '如何办理门禁卡或补办门禁卡？',
    answer:
      '业主可携带身份证明和房屋证明到物业服务中心办理门禁卡。补办时需登记遗失信息并按小区标准缴纳工本费。',
    category: '生活服务',
    keywords: ['门禁卡', '补办', '工本费'],
    viewCount: 890,
    askCount: 125,
    status: '已发布',
    source: '门禁管理制度',
    updatedAt: '2026-03-28'
  },
  {
    id: 14,
    question: '快递柜故障或包裹无法取出怎么办？',
    answer:
      '快递柜故障请先联系柜体客服并记录柜号，也可向物业前台反馈。涉及包裹安全的问题，物业会协助联系快递员和柜体运维人员处理。',
    category: '生活服务',
    keywords: ['快递柜', '包裹', '故障'],
    viewCount: 706,
    askCount: 84,
    status: '已发布',
    source: '便民设施服务说明',
    updatedAt: '2026-02-21'
  },
  {
    id: 15,
    question: '小区公共活动室如何预约？',
    answer:
      '公共活动室可通过社区小程序预约，选择日期、时段和使用人数后提交申请。物业审核通过后，请按预约时段使用并保持场地整洁。',
    category: '生活服务',
    keywords: ['活动室', '预约', '社区服务'],
    viewCount: 512,
    askCount: 66,
    status: '草稿',
    source: '社区活动室使用规定',
    updatedAt: '2026-01-30'
  },
  {
    id: 16,
    question: '对物业服务不满意如何投诉？',
    answer:
      '您可以通过小程序“投诉建议”、物业服务热线或服务中心现场提交投诉。请尽量提供时间、地点、事项和相关照片，物业会在规定时间内反馈处理进展。',
    category: '投诉建议',
    keywords: ['投诉', '服务质量', '处理进展'],
    viewCount: 1168,
    askCount: 205,
    status: '已发布',
    source: '客户投诉处理流程',
    updatedAt: '2026-04-06'
  },
  {
    id: 17,
    question: '噪音扰民应该如何反馈？',
    answer:
      '噪音扰民可先记录发生时间、位置和类型，并通过投诉建议入口提交。物业将安排秩序人员现场核实，必要时协助联系社区或相关执法部门。',
    category: '投诉建议',
    keywords: ['噪音', '扰民', '秩序维护'],
    viewCount: 998,
    askCount: 183,
    status: '已发布',
    source: '秩序维护处理指引',
    updatedAt: '2026-03-24'
  },
  {
    id: 18,
    question: '投诉提交后多久会回复？',
    answer:
      '一般投诉建议会在 1 个工作日内受理，复杂事项会同步处理计划和预计反馈时间。您可在“我的反馈”中查看处理状态和管理员回复。',
    category: '投诉建议',
    keywords: ['反馈时效', '处理状态', '管理员回复'],
    viewCount: 620,
    askCount: 79,
    status: '已发布',
    source: '客户反馈服务承诺',
    updatedAt: '2026-02-13'
  },
  {
    id: 19,
    question: '电梯故障被困如何求助？',
    answer:
      '如遇电梯故障被困，请保持冷静，按下电梯内紧急呼叫按钮并拨打物业值班电话。请勿强行扒门，物业和维保单位会立即联动处置。',
    category: '报修服务',
    keywords: ['电梯', '被困', '紧急求助'],
    viewCount: 1430,
    askCount: 232,
    status: '已发布',
    source: '电梯应急预案',
    updatedAt: '2026-04-14'
  },
  {
    id: 20,
    question: '地下车库充电桩如何申请使用？',
    answer:
      '申请充电桩需先确认车位产权或租赁关系，并向物业提交安装申请、车辆信息和用电资料。物业会结合消防、电力和车库条件进行审核。',
    category: '停车管理',
    keywords: ['充电桩', '地下车库', '申请'],
    viewCount: 760,
    askCount: 96,
    status: '待审核',
    source: '新能源充电设施管理要求',
    updatedAt: '2026-03-16'
  }
]

export const hotQuestions = [
  '物业费可以通过哪些方式缴纳？',
  '家中漏水应该如何报修？',
  '小区停车位如何办理月租？',
  '装修前需要办理哪些手续？',
  '对物业服务不满意如何投诉？',
  '电梯故障被困如何求助？'
]

export const chatHistory = [
  {
    id: 1,
    time: '2026-04-29 09:18',
    question: '物业费可以线上缴吗？',
    answer: '可以通过社区小程序、银行代扣或线上支付入口缴纳物业费。',
    category: '物业缴费',
    hit: true,
    needManual: false
  },
  {
    id: 2,
    time: '2026-04-28 16:42',
    question: '厨房漏水晚上能报修吗？',
    answer: '紧急漏水请先关闭水阀并拨打物业 24 小时值班电话。',
    category: '报修服务',
    hit: true,
    needManual: true
  },
  {
    id: 3,
    time: '2026-04-27 11:06',
    question: '朋友临时停车怎么登记？',
    answer: '业主可在访客系统登记车牌和访问时间，门岗核验后放行。',
    category: '停车管理',
    hit: true,
    needManual: false
  },
  {
    id: 4,
    time: '2026-04-25 14:30',
    question: '周日可以电钻施工吗？',
    answer: '周末和法定节假日禁止产生噪声施工。',
    category: '装修管理',
    hit: true,
    needManual: false
  },
  {
    id: 5,
    time: '2026-04-22 20:10',
    question: '楼上宠物跑动太吵怎么办？',
    answer: '该问题暂未在知识库中找到明确答案，建议联系人工客服进一步核实。',
    category: '投诉建议',
    hit: false,
    needManual: true
  }
]

export const feedbackList = [
  {
    id: 1,
    userQuestion: '物业费可以线上缴吗？',
    aiAnswer: '可以通过社区小程序、银行代扣或线上支付入口缴纳物业费。',
    feedbackType: '有帮助',
    suggestion: '回答清楚，建议补充电子发票入口。',
    status: '处理中',
    category: '物业缴费',
    similarity: 0.92,
    createdAt: '2026-04-29 10:05',
    adminReply: '已收到建议，正在补充票据相关说明。',
    time: '2026-04-29 10:05',
    question: '物业费可以线上缴吗？',
    type: '有帮助',
    reply: '已收到建议，正在补充票据相关说明。'
  },
  {
    id: 2,
    userQuestion: '厨房漏水晚上能报修吗？',
    aiAnswer: '紧急漏水请先关闭水阀并拨打物业 24 小时值班电话。',
    feedbackType: '需要人工',
    suggestion: '希望能显示紧急联系电话。',
    status: '已处理',
    category: '报修服务',
    similarity: 0.95,
    createdAt: '2026-04-28 17:12',
    adminReply: '已在报修答案中增加 24 小时值班电话提示。',
    time: '2026-04-28 17:12',
    question: '厨房漏水晚上能报修吗？',
    type: '需要人工处理',
    reply: '已在报修答案中增加 24 小时值班电话提示。'
  },
  {
    id: 3,
    userQuestion: '装修垃圾如何清运？',
    aiAnswer: '装修垃圾应袋装后放置在物业指定临时堆放点。',
    feedbackType: '没帮助',
    suggestion: '没有说明具体堆放点位置。',
    status: '待处理',
    category: '装修管理',
    similarity: 0.86,
    createdAt: '2026-04-26 09:46',
    adminReply: '暂无回复',
    time: '2026-04-26 09:46',
    question: '装修垃圾如何清运？',
    type: '没帮助',
    reply: '暂无回复'
  },
  {
    id: 4,
    userQuestion: '快递柜故障或包裹无法取出怎么办？',
    aiAnswer: '快递柜故障请先联系柜体客服并记录柜号，也可向物业前台反馈。',
    feedbackType: '有帮助',
    suggestion: '流程比较完整。',
    status: '已忽略',
    category: '生活服务',
    similarity: 0.89,
    createdAt: '2026-04-21 13:35',
    adminReply: '感谢反馈，暂不调整该条知识。',
    time: '2026-04-21 13:35',
    question: '快递柜故障或包裹无法取出怎么办？',
    type: '有帮助',
    reply: '感谢反馈，暂不调整该条知识。'
  },
  {
    id: 5,
    userQuestion: '车牌识别总是失败怎么办？',
    aiAnswer: '请联系门岗人工核验，并检查车牌是否已登记、是否欠费或录入错误。',
    feedbackType: '没帮助',
    suggestion: '希望补充线上修改车牌信息的路径。',
    status: '处理中',
    category: '停车管理',
    similarity: 0.81,
    createdAt: '2026-04-20 08:55',
    adminReply: '已转停车场管理员核对系统操作步骤。',
    time: '2026-04-20 08:55',
    question: '车牌识别总是失败怎么办？',
    type: '没帮助',
    reply: '已转停车场管理员核对系统操作步骤。'
  },
  {
    id: 6,
    userQuestion: '周末可以装修打孔吗？',
    aiAnswer: '周末和法定节假日禁止产生噪声施工。',
    feedbackType: '有帮助',
    suggestion: '建议写明是否可以无噪声施工。',
    status: '已处理',
    category: '装修管理',
    similarity: 0.94,
    createdAt: '2026-04-18 15:20',
    adminReply: '已补充无噪声施工需提前报备说明。',
    time: '2026-04-18 15:20',
    question: '周末可以装修打孔吗？',
    type: '有帮助',
    reply: '已补充无噪声施工需提前报备说明。'
  },
  {
    id: 7,
    userQuestion: '楼道堆放杂物怎么投诉？',
    aiAnswer: '可通过投诉建议入口提交，物业将安排秩序人员核实处理。',
    feedbackType: '需要人工',
    suggestion: '现场情况比较紧急，影响消防通道。',
    status: '待处理',
    category: '投诉建议',
    similarity: 0.76,
    createdAt: '2026-04-17 19:40',
    adminReply: '暂无回复',
    time: '2026-04-17 19:40',
    question: '楼道堆放杂物怎么投诉？',
    type: '需要人工处理',
    reply: '暂无回复'
  },
  {
    id: 8,
    userQuestion: '活动室预约后可以取消吗？',
    aiAnswer: '公共活动室可通过社区小程序预约，审核通过后按预约时段使用。',
    feedbackType: '没帮助',
    suggestion: '没有回答取消预约的规则。',
    status: '处理中',
    category: '生活服务',
    similarity: 0.63,
    createdAt: '2026-04-16 11:25',
    adminReply: '正在补充活动室取消预约规则。',
    time: '2026-04-16 11:25',
    question: '活动室预约后可以取消吗？',
    type: '没帮助',
    reply: '正在补充活动室取消预约规则。'
  }
]

export const chatLogs = [
  {
    id: 1,
    username: 'user',
    question: '物业费可以线上缴吗？',
    answer: '可以通过社区小程序、银行代扣或线上支付入口缴纳物业费。',
    category: '物业缴费',
    similarity: 0.92,
    hitStatus: '已命中',
    needHuman: false,
    responseTime: 0.62,
    createdAt: '2026-04-29 09:18'
  },
  {
    id: 2,
    username: '张女士',
    question: '厨房漏水晚上能报修吗？',
    answer: '紧急漏水请先关闭水阀并拨打物业 24 小时值班电话。',
    category: '报修服务',
    similarity: 0.95,
    hitStatus: '已命中',
    needHuman: true,
    responseTime: 0.58,
    createdAt: '2026-04-28 16:42'
  },
  {
    id: 3,
    username: '李先生',
    question: '朋友临时停车怎么登记？',
    answer: '业主可在访客系统登记车牌和访问时间，门岗核验后放行。',
    category: '停车管理',
    similarity: 0.9,
    hitStatus: '已命中',
    needHuman: false,
    responseTime: 0.71,
    createdAt: '2026-04-27 11:06'
  },
  {
    id: 4,
    username: '王女士',
    question: '周日可以电钻施工吗？',
    answer: '周末和法定节假日禁止产生噪声施工。',
    category: '装修管理',
    similarity: 0.93,
    hitStatus: '已命中',
    needHuman: false,
    responseTime: 0.64,
    createdAt: '2026-04-25 14:30'
  },
  {
    id: 5,
    username: '赵先生',
    question: '楼上宠物跑动太吵怎么办？',
    answer: '该问题暂未在知识库中找到明确答案，建议联系人工客服进一步核实。',
    category: '投诉建议',
    similarity: 0.38,
    hitStatus: '未命中',
    needHuman: true,
    responseTime: 0.8,
    createdAt: '2026-04-22 20:10'
  },
  {
    id: 6,
    username: '陈女士',
    question: '门禁卡丢了在哪里补办？',
    answer: '业主可携带身份证明和房屋证明到物业服务中心办理补办。',
    category: '生活服务',
    similarity: 0.88,
    hitStatus: '已命中',
    needHuman: false,
    responseTime: 0.57,
    createdAt: '2026-04-21 10:18'
  },
  {
    id: 7,
    username: '周先生',
    question: '地下车库充电桩怎么申请？',
    answer: '需确认车位产权或租赁关系，并向物业提交安装申请和车辆信息。',
    category: '停车管理',
    similarity: 0.84,
    hitStatus: '已命中',
    needHuman: true,
    responseTime: 0.76,
    createdAt: '2026-04-20 13:55'
  },
  {
    id: 8,
    username: '刘女士',
    question: '物业费发票哪里开？',
    answer: '线上缴费完成后可申请电子凭证，如需纸质票据可到服务中心打印。',
    category: '物业缴费',
    similarity: 0.79,
    hitStatus: '已命中',
    needHuman: false,
    responseTime: 0.69,
    createdAt: '2026-04-19 09:28'
  },
  {
    id: 9,
    username: '孙先生',
    question: '公共走廊灯不亮了谁来修？',
    answer: '可在公共报修中提交位置，物业工程人员会安排巡检维修。',
    category: '报修服务',
    similarity: 0.91,
    hitStatus: '已命中',
    needHuman: false,
    responseTime: 0.54,
    createdAt: '2026-04-18 18:34'
  },
  {
    id: 10,
    username: '何女士',
    question: '活动室预约后怎么取消？',
    answer: '该问题暂未在知识库中找到明确答案，建议联系人工客服进一步核实。',
    category: '生活服务',
    similarity: 0.43,
    hitStatus: '未命中',
    needHuman: true,
    responseTime: 0.82,
    createdAt: '2026-04-16 11:25'
  },
  {
    id: 11,
    username: '吴先生',
    question: '投诉提交后多久回复？',
    answer: '一般投诉建议会在 1 个工作日内受理，复杂事项会同步处理计划。',
    category: '投诉建议',
    similarity: 0.87,
    hitStatus: '已命中',
    needHuman: false,
    responseTime: 0.61,
    createdAt: '2026-04-15 16:02'
  },
  {
    id: 12,
    username: '郑女士',
    question: '装修人员进小区需要登记吗？',
    answer: '装修前需提交施工人员信息，审核后按装修管理要求进场。',
    category: '装修管理',
    similarity: 0.83,
    hitStatus: '已命中',
    needHuman: false,
    responseTime: 0.73,
    createdAt: '2026-04-14 08:50'
  }
]

export const dashboardData = {
  overview: {
    knowledgeCount: 60,
    publishedCount: 54,
    todayConsultCount: 28,
    totalConsultCount: 2860,
    hitRate: 88,
    helpfulRate: 88,
    pendingFeedback: 3,
    needHumanCount: 6
  },
  dailyTrend: [
    { date: '04-23', consultCount: 21, feedbackCount: 4 },
    { date: '04-24', consultCount: 24, feedbackCount: 3 },
    { date: '04-25', consultCount: 31, feedbackCount: 5 },
    { date: '04-26', consultCount: 27, feedbackCount: 4 },
    { date: '04-27', consultCount: 34, feedbackCount: 6 },
    { date: '04-28', consultCount: 30, feedbackCount: 5 },
    { date: '04-29', consultCount: 28, feedbackCount: 4 }
  ],
  hotQuestions: [
    { question: '物业费可以通过哪些方式缴纳？', count: 216 },
    { question: '家中漏水应该如何报修？', count: 311 },
    { question: '小区停车位如何办理月租？', count: 265 },
    { question: '装修前需要办理哪些手续？', count: 244 },
    { question: '对物业服务不满意如何投诉？', count: 205 }
  ],
  categoryRatio: [
    { name: '物业缴费', value: 22 },
    { name: '报修服务', value: 28 },
    { name: '停车管理', value: 18 },
    { name: '装修管理', value: 15 },
    { name: '生活服务', value: 9 },
    { name: '投诉建议', value: 8 }
  ],
  feedbackStatus: [
    { status: '待处理', count: 2 },
    { status: '处理中', count: 3 },
    { status: '已处理', count: 2 },
    { status: '已忽略', count: 1 }
  ],
  hitRateTrend: [
    { date: '04-23', hitRate: 84 },
    { date: '04-24', hitRate: 86 },
    { date: '04-25', hitRate: 87 },
    { date: '04-26', hitRate: 85 },
    { date: '04-27', hitRate: 89 },
    { date: '04-28', hitRate: 88 },
    { date: '04-29', hitRate: 88 }
  ],
  unmatchedQuestions: [
    { question: '活动室预约后怎么取消？', count: 6, category: '生活服务' },
    { question: '楼上宠物跑动太吵怎么办？', count: 5, category: '投诉建议' },
    { question: '充电桩排队多久能安装？', count: 4, category: '停车管理' },
    { question: '小区团购摊位如何申请？', count: 3, category: '生活服务' }
  ]
}

export const vectorStatus = {
  status: '运行中',
  knowledgeCount: 60,
  lastBuildTime: '2026-04-29 09:30',
  vectorStore: 'Property-QA-VectorStore',
  embeddingModel: 'text-embedding-3-small',
  ragStatus: {
    indexStatus: '已同步',
    chunkCount: 186,
    avgSimilarity: 0.82,
    lastSyncResult: '成功',
    pendingSyncCount: 2
  }
}
