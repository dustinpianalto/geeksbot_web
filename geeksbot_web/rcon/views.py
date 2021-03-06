import asyncio

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .rcon_lib import arcon

from .models import RconServer
from .utils import create_error_response, create_success_response, create_rcon_response
from utils.api_utils import PaginatedAPIView
from .serializers import RconServerSerializer
from users.models import User

# Create your views here.

# API Views


class RCONServersAPI(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, format=None):
        servers = RconServer.get_guild_servers(guild_id)
        page = self.paginate_queryset(servers)
        if page:
            return create_success_response(page, status.HTTP_200_OK, many=True)
        return create_success_response(servers, status.HTTP_200_OK, many=True)

    def post(self, request, guild_id, format=None):
        data = dict(request.data)
        data['guild'] = guild_id
        return RconServer.add_new_server(data)


class RCONServerDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, name, format=None):
        server = RconServer.get_server(guild_id, name)
        if server:
            return create_success_response(server, status.HTTP_200_OK, many=False)
        else:
            return create_error_response("RCON Server Does Not Exist",
                                         status=status.HTTP_404_NOT_FOUND)

    def put(self, request, guild_id, name, format=None):
        data = dict(request.data)
        server = RconServer.get_server(guild_id, name)
        if server:
            return server.update_server(data)
        else:
            return create_error_response('RCON Server Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)


class ListPlayers(PaginatedAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, guild_id, name, format=None):
        server: RconServer = RconServer.get_server(guild_id, name)
        if server:
            ark = arcon.ARKServer(host=server.ip, port=server.port, password=server.password)
            connected = ark.connect()
            if connected == 1:
                resp = ark.listplayers()
                return create_rcon_response(resp, status=status.HTTP_200_OK)
            else:
                return create_error_response('Connection failure',
                                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return create_error_response('RCON Server Does Not Exist',
                                     status=status.HTTP_404_NOT_FOUND)


class WhitelistAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, guild_id, name, format=None):
        discord_id = request.data.get('discord_id')
        if not discord_id:
            return create_error_response("A Discord ID is required",
                                         status=status.HTTP_400_BAD_REQUEST)
        user = User.get_user_by_id(discord_id)
        if not user.steam_id:
            return create_error_response('The User must have a Steam ID in the database in order to whitelist them.',
                                         status=status.HTTP_400_BAD_REQUEST)
        server: RconServer = RconServer.get_server(guild_id, name)
        if not server:
            return create_error_response('RCON Server Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)
        ark = arcon.ARKServer(host=server.ip, port=server.port, password=server.password)
        connected = ark.connect()
        if not connected == 1:
            return create_error_response('Connection Failure',
                                         status=status.HTTP_408_REQUEST_TIMEOUT)
        resp = ark.whitelist(user.steam_id)
        return create_rcon_response(resp, status=status.HTTP_200_OK)


class BroadcastAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, guild_id, name, format=None):
        message = request.data.get('message')
        if not message:
            return create_error_response('A message is required',
                                         status=status.HTTP_400_BAD_REQUEST)
        server: RconServer = RconServer.get_server(guild_id, name)
        if not server:
            return create_error_response('RCON Server Does Not Exist',
                                         status=status.HTTP_404_NOT_FOUND)
        ark = arcon.ARKServer(host=server.ip, port=server.port, password=server.password)
        connected = ark.connect()
        if not connected == 1:
            return create_error_response('Connection Failure',
                                         status=status.HTTP_408_REQUEST_TIMEOUT)
        resp = ark.broadcast(message)
        return create_rcon_response(resp, status=status.HTTP_200_OK)
