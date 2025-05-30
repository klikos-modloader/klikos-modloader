class Data:
    class BloxstrapRPC:
        prefix: str = "[FLog::Output]"
        startswith: str = "[BloxstrapRPC]"


    class Player:
        class GameID:
            prefix: str = "[FLog::Output]"
            startswith: str = "! Joining game "


        class Join:
            prefix: str = "[FLog::GameJoinLoadTime]"
            startswith: str = "Report game_join_loadtime"


        class Leave:
            prefix: str = "[FLog::SingleSurfaceApp]"
            message: str = "leaveUGCGameInternal"


        class Exit:
            prefix: str = "[FLog::SingleSurfaceApp]"
            message: str = "unregisterMemoryPrioritizationCallback"


    class Studio:
        class Join:
            prefix: str = "[FLog::StudioKeyEvents]"
            startswith: str = "open place"


        class Leave:
            prefix: str = "[FLog::StudioKeyEvents]"
            message: str = "close IDE doc"


        class Exit:
            prefix: str = "[FLog::Output]"
            message: str = "About to exit the application, doing cleanup."