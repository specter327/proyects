class Device:
    def __init__(self,
        createdAt: str,
        deletedAt: str,
        id: str,
        lastSeen: str,
        name: str,
        updatedAt: str
    ) -> None:
        # Instance property assigment
        self.createdAt = createdAt
        self.deletedAt = deletedAt
        self.id = id
        self.lastSeen = lastSeen
        self.name = name
        self.updatedAt = updatedAt
