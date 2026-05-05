from datetime import datetime

from werkzeug.security import generate_password_hash

from app import app
from extensions.db import db
from models.category import Category
from models.qa import QaKnowledge
from models.user import User


USERS = [
    {
        "username": "user",
        "email": "user@example.com",
        "password": "123456",
        "role": "user",
        "nickname": "普通用户",
    },
    {
        "username": "admin",
        "email": "admin@example.com",
        "password": "123456",
        "role": "admin",
        "nickname": "系统管理员",
    },
]


CATEGORIES = [
    {
        "name": "物业缴费",
        "description": "物业费、水电公摊、账单查询、票据开具等缴费相关知识。",
        "sort_order": 1,
    },
    {
        "name": "报修服务",
        "description": "室内报修、公共区域维修、电梯故障、紧急抢修等服务流程。",
        "sort_order": 2,
    },
    {
        "name": "停车管理",
        "description": "月租车位、临停登记、车牌识别、充电桩申请等停车业务。",
        "sort_order": 3,
    },
    {
        "name": "装修管理",
        "description": "装修申请、施工时间、垃圾清运、施工人员进场等管理规范。",
        "sort_order": 4,
    },
    {
        "name": "生活服务",
        "description": "门禁卡、快递柜、活动室预约、社区便民服务等日常事项。",
        "sort_order": 5,
    },
    {
        "name": "投诉建议",
        "description": "服务投诉、噪音扰民、环境秩序、处理进度查询等反馈事项。",
        "sort_order": 6,
    },
]


QA_ITEMS = [
    {
        "question": "物业费可以通过哪些方式缴纳？",
        "answer": "您可以通过物业服务中心现场缴费、社区小程序、银行代扣或线上支付入口缴纳物业费。线上缴费完成后系统会自动生成电子凭证，如需纸质票据可到服务中心申请打印。",
        "category": "物业缴费",
        "keywords": ["物业费", "缴费方式", "线上支付"],
        "viewCount": 1280,
        "askCount": 216,
        "status": "已发布",
        "source": "物业收费管理制度",
        "updatedAt": "2026-04-10",
    },
    {
        "question": "物业费逾期会产生滞纳金吗？",
        "answer": "物业费建议按缴费周期及时缴纳。是否产生滞纳金以物业服务合同和小区公告为准，如遇特殊情况可提前联系管家登记说明。",
        "category": "物业缴费",
        "keywords": ["逾期", "滞纳金", "合同"],
        "viewCount": 940,
        "askCount": 137,
        "status": "已发布",
        "source": "物业服务合同",
        "updatedAt": "2026-03-18",
    },
    {
        "question": "如何查询物业缴费明细？",
        "answer": "登录社区小程序后进入“我的账单”，可按房号、月份和费用类型查询缴费明细。若明细与实际情况不一致，请携带房产证明或租赁证明联系服务中心核对。",
        "category": "物业缴费",
        "keywords": ["账单", "明细", "查询"],
        "viewCount": 728,
        "askCount": 103,
        "status": "已发布",
        "source": "线上缴费操作手册",
        "updatedAt": "2026-03-05",
    },
    {
        "question": "家中漏水应该如何报修？",
        "answer": "发现漏水请先关闭相关水阀并保护现场，可通过小程序提交报修，上传照片并填写房号、联系人和故障位置。紧急情况请拨打物业 24 小时值班电话，维修人员会优先处理。",
        "category": "报修服务",
        "keywords": ["漏水", "报修", "紧急维修"],
        "viewCount": 1624,
        "askCount": 311,
        "status": "已发布",
        "source": "工程报修服务规范",
        "updatedAt": "2026-04-12",
    },
    {
        "question": "公共区域照明损坏怎么处理？",
        "answer": "公共区域照明损坏可在“公共报修”中选择楼栋、楼层和位置提交，也可告知楼栋管家。物业工程人员会在受理后安排巡检维修。",
        "category": "报修服务",
        "keywords": ["公共区域", "照明", "工程维修"],
        "viewCount": 684,
        "askCount": 88,
        "status": "已发布",
        "source": "公共设施巡检制度",
        "updatedAt": "2026-02-26",
    },
    {
        "question": "报修后多久会有人联系？",
        "answer": "普通报修一般在 30 分钟内完成受理并联系业主，紧急报修将优先响应。具体上门时间会结合维修类型、配件情况和业主预约时间确认。",
        "category": "报修服务",
        "keywords": ["响应时间", "上门", "维修"],
        "viewCount": 810,
        "askCount": 142,
        "status": "已发布",
        "source": "客户服务响应标准",
        "updatedAt": "2026-03-22",
    },
    {
        "question": "小区停车位如何办理月租？",
        "answer": "办理月租车位需携带身份证、行驶证和房屋证明到物业服务中心登记，也可在线提交车辆信息。审核通过后按月缴纳停车费用并录入车牌识别系统。",
        "category": "停车管理",
        "keywords": ["停车位", "月租", "车牌"],
        "viewCount": 1510,
        "askCount": 265,
        "status": "已发布",
        "source": "停车场管理办法",
        "updatedAt": "2026-04-08",
    },
    {
        "question": "临时车辆如何进入小区？",
        "answer": "临时车辆需由业主提前在访客系统中登记车牌和访问时间，或到门岗说明来访信息。门岗核验后按临停规则放行，超时可能产生临停费用。",
        "category": "停车管理",
        "keywords": ["临时车辆", "访客", "门岗"],
        "viewCount": 1018,
        "askCount": 177,
        "status": "已发布",
        "source": "访客车辆通行规则",
        "updatedAt": "2026-03-30",
    },
    {
        "question": "车牌识别失败怎么办？",
        "answer": "车牌识别失败时请联系门岗人工核验，并检查车牌是否已完成登记、是否欠费或是否存在录入错误。确认后物业可协助更新车牌信息。",
        "category": "停车管理",
        "keywords": ["车牌识别", "门禁", "欠费"],
        "viewCount": 650,
        "askCount": 91,
        "status": "已发布",
        "source": "车场系统运维手册",
        "updatedAt": "2026-02-18",
    },
    {
        "question": "装修前需要办理哪些手续？",
        "answer": "装修前需到物业服务中心提交装修申请、施工图纸、施工人员信息和业主身份证明，签署装修管理协议并缴纳相关保证金后方可进场施工。",
        "category": "装修管理",
        "keywords": ["装修申请", "施工图纸", "保证金"],
        "viewCount": 1386,
        "askCount": 244,
        "status": "已发布",
        "source": "装修管理协议",
        "updatedAt": "2026-04-01",
    },
    {
        "question": "装修施工时间有什么规定？",
        "answer": "装修施工时间通常为工作日 8:30-12:00、14:00-18:00，周末和法定节假日禁止产生噪声施工。具体时间以小区装修管理公示为准。",
        "category": "装修管理",
        "keywords": ["施工时间", "噪声", "节假日"],
        "viewCount": 1134,
        "askCount": 198,
        "status": "已发布",
        "source": "小区装修公示",
        "updatedAt": "2026-03-19",
    },
    {
        "question": "装修垃圾如何清运？",
        "answer": "装修垃圾应袋装后放置在物业指定临时堆放点，严禁堆放在楼道、电梯厅和消防通道。清运费用和时间安排可咨询物业服务中心。",
        "category": "装修管理",
        "keywords": ["装修垃圾", "清运", "消防通道"],
        "viewCount": 779,
        "askCount": 118,
        "status": "已发布",
        "source": "装修垃圾清运指引",
        "updatedAt": "2026-03-11",
    },
    {
        "question": "如何办理门禁卡或补办门禁卡？",
        "answer": "业主可携带身份证明和房屋证明到物业服务中心办理门禁卡。补办时需登记遗失信息并按小区标准缴纳工本费。",
        "category": "生活服务",
        "keywords": ["门禁卡", "补办", "工本费"],
        "viewCount": 890,
        "askCount": 125,
        "status": "已发布",
        "source": "门禁管理制度",
        "updatedAt": "2026-03-28",
    },
    {
        "question": "快递柜故障或包裹无法取出怎么办？",
        "answer": "快递柜故障请先联系柜体客服并记录柜号，也可向物业前台反馈。涉及包裹安全的问题，物业会协助联系快递员和柜体运维人员处理。",
        "category": "生活服务",
        "keywords": ["快递柜", "包裹", "故障"],
        "viewCount": 706,
        "askCount": 84,
        "status": "已发布",
        "source": "便民设施服务说明",
        "updatedAt": "2026-02-21",
    },
    {
        "question": "小区公共活动室如何预约？",
        "answer": "公共活动室可通过社区小程序预约，选择日期、时段和使用人数后提交申请。物业审核通过后，请按预约时段使用并保持场地整洁。",
        "category": "生活服务",
        "keywords": ["活动室", "预约", "社区服务"],
        "viewCount": 512,
        "askCount": 66,
        "status": "草稿",
        "source": "社区活动室使用规定",
        "updatedAt": "2026-01-30",
    },
    {
        "question": "对物业服务不满意如何投诉？",
        "answer": "您可以通过小程序“投诉建议”、物业服务热线或服务中心现场提交投诉。请尽量提供时间、地点、事项和相关照片，物业会在规定时间内反馈处理进展。",
        "category": "投诉建议",
        "keywords": ["投诉", "服务质量", "处理进展"],
        "viewCount": 1168,
        "askCount": 205,
        "status": "已发布",
        "source": "客户投诉处理流程",
        "updatedAt": "2026-04-06",
    },
    {
        "question": "噪音扰民应该如何反馈？",
        "answer": "噪音扰民可先记录发生时间、位置和类型，并通过投诉建议入口提交。物业将安排秩序人员现场核实，必要时协助联系社区或相关执法部门。",
        "category": "投诉建议",
        "keywords": ["噪音", "扰民", "秩序维护"],
        "viewCount": 998,
        "askCount": 183,
        "status": "已发布",
        "source": "秩序维护处理指引",
        "updatedAt": "2026-03-24",
    },
    {
        "question": "投诉提交后多久会回复？",
        "answer": "一般投诉建议会在 1 个工作日内受理，复杂事项会同步处理计划和预计反馈时间。您可在“我的反馈”中查看处理状态和管理员回复。",
        "category": "投诉建议",
        "keywords": ["反馈时效", "处理状态", "管理员回复"],
        "viewCount": 620,
        "askCount": 79,
        "status": "已发布",
        "source": "客户反馈服务承诺",
        "updatedAt": "2026-02-13",
    },
    {
        "question": "电梯故障被困如何求助？",
        "answer": "如遇电梯故障被困，请保持冷静，按下电梯内紧急呼叫按钮并拨打物业值班电话。请勿强行扒门，物业和维保单位会立即联动处置。",
        "category": "报修服务",
        "keywords": ["电梯", "被困", "紧急求助"],
        "viewCount": 1430,
        "askCount": 232,
        "status": "已发布",
        "source": "电梯应急预案",
        "updatedAt": "2026-04-14",
    },
    {
        "question": "地下车库充电桩如何申请使用？",
        "answer": "申请充电桩需先确认车位产权或租赁关系，并向物业提交安装申请、车辆信息和用电资料。物业会结合消防、电力和车库条件进行审核。",
        "category": "停车管理",
        "keywords": ["充电桩", "地下车库", "申请"],
        "viewCount": 760,
        "askCount": 96,
        "status": "待审核",
        "source": "新能源充电设施管理要求",
        "updatedAt": "2026-03-16",
    },
]


def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d")


def seed_users():
    inserted = 0
    for item in USERS:
        exists = User.query.filter(
            (User.username == item["username"]) | (User.email == item["email"])
        ).first()
        if exists:
            continue

        db.session.add(
            User(
                username=item["username"],
                email=item["email"],
                password_hash=generate_password_hash(item["password"]),
                role=item["role"],
                nickname=item["nickname"],
                status="启用",
            )
        )
        inserted += 1

    db.session.commit()
    return inserted


def seed_categories():
    inserted = 0
    for item in CATEGORIES:
        if Category.query.filter_by(name=item["name"]).first():
            continue

        db.session.add(
            Category(
                name=item["name"],
                description=item["description"],
                sort_order=item["sort_order"],
                status="启用",
            )
        )
        inserted += 1

    db.session.commit()
    return inserted


def seed_qa():
    admin = User.query.filter_by(username="admin").first()
    admin_id = admin.id if admin else None
    inserted = 0

    for item in QA_ITEMS:
        if QaKnowledge.query.filter_by(question=item["question"]).first():
            continue

        updated_at = parse_date(item["updatedAt"])
        db.session.add(
            QaKnowledge(
                question=item["question"],
                answer=item["answer"],
                category=item["category"],
                keywords=",".join(item["keywords"]),
                view_count=item["viewCount"],
                ask_count=item["askCount"],
                status=item["status"],
                source=item["source"],
                created_by=admin_id,
                updated_by=admin_id,
                created_at=updated_at,
                updated_at=updated_at,
            )
        )
        inserted += 1

    db.session.commit()
    return inserted


def refresh_category_counts():
    for category in Category.query.all():
        category.question_count = QaKnowledge.query.filter(
            QaKnowledge.category == category.name,
            QaKnowledge.status != "已停用",
        ).count()
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        user_count = seed_users()
        category_count = seed_categories()
        qa_count = seed_qa()
        refresh_category_counts()

        print(f"用户初始化完成，新增 {user_count} 个")
        print(f"分类初始化完成，新增 {category_count} 个")
        print(f"问答初始化完成，新增 {qa_count} 条")

