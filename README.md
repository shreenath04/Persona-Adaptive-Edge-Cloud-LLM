# Persona-Adaptive-Edge-Cloud-LLM
A dual-model AI assistant that adapts to user style and complexity, deciding in real time whether to run locally or in the cloud.

🔐 Current Deployment Note:
Although the system supports real cloud execution, the “cloud model” is presently running locally via Ollama. This avoids unexpected token costs during development while preserving the same architectural behavior. Once deployed, the larger model can be swapped to a real cloud endpoint with zero code changes.

🚀 DualBrain AI

A Persona-Aware Hybrid Local + Cloud LLM System with Smart Routing

DualBrain AI is an intelligent chat system that dynamically decides where and how to generate responses — either using a local lightweight model (Gemma 4B) for fast, simple requests or a cloud-grade model (Llama 3.1 8B) for complex reasoning and long-form generation.

It adapts to each user by learning their style during onboarding and automatically tailoring responses to their tone, skill level, and preferred format.

🧠 Why This Project?

Most AI systems today are either:

⚙️ Fully local — fast and private, but limited in reasoning power
☁️ Fully cloud-based — powerful, but requires strong networking and compute

DualBrain AI combines the best of both.

It intelligently routes each query to the most suitable model based on:
	- Query length & complexity
	- User expertise level
	- Response expectations
	 -Persona preferences (tone, structure, format)

This reduces unnecessary cloud usage, improves latency, and creates a personal, adaptive assistant.

✨ Key Features

🧩 User Authentication: Secure login/signup with hashed passwords and persistent stored traits
🎭 Persona Extraction: The system converts raw user descriptions into structured personality traits via LLM
🔀 Smart Model Routing:Automatic decision between local LLM and cloud LLM based on request complexity
💻 Offline Capability: Local responses work even without internet
☁️ Cloud AI for Complexity: Heavy tasks, essays, research, and multi-step reasoning are routed to the cloud
🧠 Adaptive Prompting: Prompts are rewritten based on tone preference, expertise level, and style
📁 MongoDB Storage: Stores user profiles, raw descriptions, login timestamps, and trait JSON

🔧 Tech Stack

Language: Python
Local LLM: gemma3:4b via Ollama
Cloud LLM: llama3.1:8b via Ollama
Database: MongoDB

Auth: bcrypt hashing
Execution: CLI-based UX



🔧 Future Work

The current system successfully performs adaptive routing, authentication, and persona-based prompt shaping, but several enhancements are planned to evolve DualBrain AI into a fully personalized assistant experience:

🧠 1. Dynamic Trait Updating

Right now, user traits are inferred once during onboarding. The next phase will enable continuous learning, where the system updates personality traits, tone preferences, and expertise level based on real conversational patterns.
💬 2. Long-Term Conversational Memory

🎨 3. Front-End UI + Deployment
