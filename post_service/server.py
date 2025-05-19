from concurrent import futures
import grpc
import post_service_pb2
import post_service_pb2_grpc
from services.post_service import PostService
from models.database import get_db, Base, engine

def serve():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_service_pb2_grpc.add_PostServiceServicer_to_server(
        PostServiceServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

class PostServiceServicer(post_service_pb2_grpc.PostServiceServicer):
    def __init__(self):
        self.db = next(get_db())

    def CreatePost(self, request, context):
        try:
            post_service = PostService(self.db)
            post = post_service.create_post(request)
            return post_service_pb2.PostResponse(post=post)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_service_pb2.PostResponse()

    def GetPost(self, request, context):
        try:
            post_service = PostService(self.db)
            post = post_service.get_post(request)
            return post_service_pb2.PostResponse(post=post)
        except ValueError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return post_service_pb2.PostResponse()
        except PermissionError as e:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details(str(e))
            return post_service_pb2.PostResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_service_pb2.PostResponse()

    def UpdatePost(self, request, context):
        try:
            post_service = PostService(self.db)
            post = post_service.update_post(request)
            return post_service_pb2.PostResponse(post=post)
        except ValueError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return post_service_pb2.PostResponse()
        except PermissionError as e:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details(str(e))
            return post_service_pb2.PostResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_service_pb2.PostResponse()

    def DeletePost(self, request, context):
        try:
            post_service = PostService(self.db)
            success = post_service.delete_post(request)
            return post_service_pb2.DeletePostResponse(success=success)
        except ValueError as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
            return post_service_pb2.DeletePostResponse(success=False)
        except PermissionError as e:
            context.set_code(grpc.StatusCode.PERMISSION_DENIED)
            context.set_details(str(e))
            return post_service_pb2.DeletePostResponse(success=False)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_service_pb2.DeletePostResponse(success=False)

    def ListPosts(self, request, context):
        try:
            post_service = PostService(self.db)
            return post_service.list_posts(request)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return post_service_pb2.ListPostsResponse()

if __name__ == "__main__":
    serve()