from services.agents import AgentCoordinator, CodeGeneratorAgent, ArchitectureAgent, TestWriterAgent, ReviewerAgent

def verify_agent_services():
    coordinator = AgentCoordinator()
    agents = [
        CodeGeneratorAgent(),
        ArchitectureAgent(),
        TestWriterAgent(),
        ReviewerAgent()
    ]
    
    for agent in agents:
        status = coordinator.verify_agent(agent)
        print(f"{agent.agent_name}: {'✅ Operational' if status else '❌ Offline'}")

if __name__ == "__main__":
    verify_agent_services()
