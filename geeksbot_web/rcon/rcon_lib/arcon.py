from . import rcon
import asyncio
from typing import Union
import logging

arcon_log = logging.getLogger('arcon_lib')


class ARKServer(rcon.RCONConnection):
    def __init__(self, *args, monitor_chat: bool = False, server_chat_channel: int = None,
                 server_messages_channel: int = None, **kwargs):
        self.monitor_chat = monitor_chat
        self.server_chat_channel = server_chat_channel
        self.server_messages_channel = server_messages_channel
        super().__init__(*args, **kwargs)

    def run_command(self, command: str, multi_packet: bool = False) \
            -> Union[rcon.RCONPacket, str]:
        arcon_log.debug(f'Command requested: {command}')
        if self.authenticated:
            packet = rcon.RCONPacket(next(self.packet_id), rcon.SERVERDATA_EXECCOMMAND, command)
            try:
                arcon_log.debug(f'Sending packet {packet.packet_id}')
                self.send_packet(packet)
                arcon_log.debug(f'Packet Sent.')
            except ConnectionResetError:
                arcon_log.info(f'Connection to {self.host}:{self.port} lost')
            finally:
                arcon_log.debug(f'Waiting for response to packet {packet.packet_id}')
                try:
                    response = self.read(packet, multi_packet=multi_packet)
                except asyncio.TimeoutError as e:
                    arcon_log.warning(f'No response received: {e}\nPlease try again later.')
                else:
                    arcon_log.debug(f'Response Received:\n{response.packet_type}:{response.packet_id}:{response.body}')
                    response.body = response.body.strip('\x00\x00').strip()
                    return response
        else:
            return 'Server is not Authenticated. Please let the Admin know of this issue.'

    def getchat(self) -> str:
        response = self.run_command(command='getchat', multi_packet=True)
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def saveworld(self) -> str:
        response = self.run_command(command='saveworld')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def serverchat(self, message: str) -> str:
        response = self.run_command(command=f'serverchat {message}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def broadcast(self, message: str) -> str:
        response = self.run_command(command=f'broadcast {message}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def listplayers(self) -> str:
        response = self.run_command(command=f'listplayers')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def whitelist(self, steam_id: str) -> str:
        response = self.run_command(command=f'AllowPlayerToJoinNoCheck {steam_id}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def ban_player(self, steam_id: int) -> str:
        response = self.run_command(command=f'BanPlayer {steam_id}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def unban_player(self, steam_id: int) -> str:
        response = self.run_command(command=f'UnbanPlayer {steam_id}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def kick_player(self, steam_id: int) -> str:
        response = self.run_command(command=f'KickPlayer {steam_id}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def stop_server(self) -> int:
        saved = self.saveworld()
        if saved == 'World Saved':
            self.serverchat(saved)
            asyncio.sleep(10)
            response = self.run_command(command='DoExit')
            if response.body == 'Exiting...':
                return 0
            else:
                return 2
        else:
            return 1

    def get_logs(self):
        response = self.run_command(command=f'GetGameLog', multi_packet=True)
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def server_chat_to_steam_id(self, steam_id: int, message: str) -> str:
        response = self.run_command(command=f'ServerChatTo {steam_id} {message}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def server_chat_to_player_name(self, player_name: str, message: str) -> str:
        response = self.run_command(command=f'ServerChatToPlayer "{player_name}" {message}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def set_time_of_day(self, hour: int, minute: int = 00, seconds: int = 00) -> str:
        response = self.run_command(command=f'SetTimeOfDay {hour}:{minute}:{seconds}')
        return response.body if isinstance(response, rcon.RCONPacket) else response

    def destroy_wild_dinos(self):
        response = self.run_command(command='DestroyWildDinos')
        return response.body if isinstance(response, rcon.RCONPacket) else response
