from models.qa import QaKnowledge


def build_document_from_qa(qa):
    from langchain_core.documents import Document

    keywords = qa.keywords or ""
    page_content = "\n".join(
        [
            f"分类：{qa.category}",
            f"问题：{qa.question}",
            f"关键词：{keywords}",
            f"标准答案：{qa.answer}",
        ]
    )

    return Document(
        page_content=page_content,
        metadata={
            "qa_id": qa.id,
            "question": qa.question,
            "category": qa.category,
            "answer": qa.answer,
            "keywords": keywords,
        },
    )


def load_published_qa_documents():
    records = (
        QaKnowledge.query.filter_by(status="已发布")
        .order_by(QaKnowledge.id.asc())
        .all()
    )
    return [build_document_from_qa(item) for item in records]
