import os
from shadai.core.session import Session

async def ingest_documents_with_alias(input_dir: str, alias: str, session) -> None:
    """
    Ingests a directory of documents into a session with a given alias.
    """

    alias = os.path.basename(input_dir)

    print(f"Starting ingestion with alias: {alias}")
    await session.ingest(input_dir=input_dir, alias="alias")


async def ingest_documents_without_alias(input_dir: str, session) -> None:
    """
    Ingests a directory of documents into a session without a given alias.
    """
    print(f"Starting ingestion without alias")
    await session.ingest(input_dir=input_dir)


async def chat_with_history(session, message: str, system_prompt: str) -> str:
    """
    Chats only with the history and returns the result.
    """
    response = await session.chat(
        message=message,
        system_prompt=system_prompt,
        use_history=True,
        display_in_console=True
    )
    # Optional cleanup of chat history
    await session.cleanup_chat()
    return response