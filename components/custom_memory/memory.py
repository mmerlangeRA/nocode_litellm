class ConversationMemory:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.memory = []

    def add(self, interaction):
        """Add a new interaction to memory."""
        if len(self.memory) >= self.capacity:
            # Remove the oldest interaction to make room for the new one
            self.memory.pop(0)
        self.memory.append(interaction)

    def retrieve(self):
        """Retrieve the entire memory."""
        return self.memory

    def forget(self):
        """Forget the oldest interaction."""
        if self.memory:
            self.memory.pop(0)
