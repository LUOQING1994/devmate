import asyncio
from client import MCPSearchClient


async def main():
    client = MCPSearchClient()

    result = await client.search("北京今天的天气")
    for r in result:
        print(r["title"])
        print(r["content"][:100])
        print("-" * 40)

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
