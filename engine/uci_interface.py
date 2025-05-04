import chess
import chess.engine
import subprocess
import os
import sys
import platform
import time

class UCIEngineInterface:
    def __init__(self, engine_path=None, depth=10, movetime=1000):
        """
        Initialize a UCI engine interface.
        
        Args:
            engine_path: Path to the UCI engine executable. If None, will use the default path.
            depth: Search depth for the engine (number of plies to look ahead)
            movetime: Time in milliseconds the engine is allowed to think
        """
        if engine_path is None:
            # Use the default engine path relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Determine the correct executable name based on platform
            if platform.system() == "Windows":
                engine_name = "uci_engine.exe"
            else:
                engine_name = "uci_engine"
                
            engine_path = os.path.join(base_dir, "cpp", engine_name)
            
        self.engine_path = engine_path
        self.depth = depth
        self.movetime = movetime
        self.engine = None
        
    def __enter__(self):
        """Support for context manager protocol"""
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when used as context manager"""
        self.close()
        
    def open(self):
        """Open a connection to the UCI engine"""
        try:
            # Start the engine process
            transport = chess.engine.SimpleEngine.popen_uci(self.engine_path)
            self.engine = transport
            
            # Set default options
            if self.depth:
                self.set_depth(self.depth)
            if self.movetime:
                self.set_movetime(self.movetime)
                
            return True
        except Exception as e:
            print(f"Error opening engine: {str(e)}")
            return False
            
    def close(self):
        """Close the connection to the UCI engine"""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
            self.engine = None
            
    def set_depth(self, depth):
        """Set the search depth"""
        if not self.engine:
            self.depth = depth  # Store for when we open the engine
            return False
            
        try:
            self.engine.configure({"Depth": depth})
            self.depth = depth
            return True
        except Exception as e:
            print(f"Error setting depth: {str(e)}")
            return False
            
    def set_movetime(self, movetime):
        """Set the move time in milliseconds"""
        if not self.engine:
            self.movetime = movetime  # Store for when we open the engine
            return False
            
        try:
            self.engine.configure({"MoveTime": movetime})
            self.movetime = movetime
            return True
        except Exception as e:
            print(f"Error setting movetime: {str(e)}")
            return False
            
    def get_best_move(self, board, depth=None, movetime=None):
        if not self.engine:
            if not self.open():
                return None, {"error": "Failed to open engine"}
                
        try:
            # Set up our search limits based on parameters
            limit_args = {}
            
            if depth is not None:
                limit_args["depth"] = depth
            elif self.depth:
                limit_args["depth"] = self.depth
                
            if movetime is not None:
                limit_args["time"] = movetime / 1000.0  # Convert ms to seconds
            elif self.movetime:
                limit_args["time"] = self.movetime / 1000.0
                
            # Create the limit object
            limit = chess.engine.Limit(**limit_args)
            
            # Get the engine's move
            start_time = time.time()
            result = self.engine.play(board, limit)
            end_time = time.time()
            
            # Extract useful information
            info = {
                "move": result.move,
                "elapsed": (end_time - start_time) * 1000,  # Convert to ms
                "ponder": result.ponder if hasattr(result, "ponder") else None,
                "depth": getattr(result, "depth", None),
                "score": getattr(result, "score", None)
            }
            
            return result.move, info
            
        except Exception as e:
            print(f"Error getting best move: {str(e)}")
            return None, {"error": str(e)}


# Simple usage example
if __name__ == "__main__":
    board = chess.Board()
    
    # Example of using as context manager
    with UCIEngineInterface(depth=5, movetime=2000) as engine:
        move, info = engine.get_best_move(board)
        print(f"Best move: {move}")
        print(f"Info: {info}")
        
    # Example of using directly
    engine = UCIEngineInterface(depth=3, movetime=1000)
    try:
        engine.open()
        move, info = engine.get_best_move(board)
        print(f"Best move: {move}")
        print(f"Info: {info}")
    finally:
        engine.close()