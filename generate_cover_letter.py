import cohere

# Your API key
API_KEY = "6QYELzaCHMKLRPK8czOan54umjgPncyqiKOzj5mo"
co = cohere.Client(API_KEY)

# Updated prompt with humanization directive
user_prompt = """
Write a professional cover letter for a Smart Contract Engineer role at DeFi Nexus Labs.

Tone Guidelines:
- Intelligent, warm, and natural — write like a thoughtful human, not a corporate robot
- Clear and concise, without unnecessary adjectives
- Confident and grounded in actual experience
- Free of inflated phrases like "I'm thrilled", "I'm passionate", or "amazing opportunity"

IMPORTANT:
Only include factual content pulled directly from the candidate summary. Do not invent or exaggerate qualifications.

Company Context:
DeFi Nexus Labs is developing DeFi primitives, flash loan strategies, MEV-resistant infrastructure, and ERC-20 tokenomics. Remote-first and async-friendly.

Candidate Summary:
Lucas Rizzo is a Web3 Engineer and DeFi Bot Developer. He has built liquidation bots with stealth transaction relays and Velora, deployed ERC-20 token ecosystems with claim automation, and led backend smart contract development in Solidity, Python, and Ethers.js. He has CompTIA Security+ certification and has worked successfully in async remote teams.

Write a concise, well-structured cover letter that demonstrates technical relevance and feels human and thoughtful.
"""

# Generate the cover letter using Cohere's chat endpoint
response = co.chat(
    model="command-r",
    message=user_prompt,
    temperature=0.7
)

# Output the result
print("\n📝 COVER LETTER:\n")
print(response.text.strip())

