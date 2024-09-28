
                    (f"{target_username} has been tipped an amount of: {tip_amount} gold.")

                    except Exception as e:
                        await self.highrise.chat(f"Error tipping {target_username}: {str(e)}")
                except Exception as e:
                    await self.highrise.chat(f"Error tipping: {str(e)}")


            elif message.startswith("/addvip"):

                try:

                    parts = message.split(" ")
                    if len(parts) != 2:
                        await self.highrise.chat("Invalid command. Usage: /addvip @{username}")
                        return

                    target_username = parts[1]
                    if not target_username.startswith('@'):
                        await self.highrise.chat("Invalid username format. Use '@{username}'.")
                        return

                    username_str = target_username[1:]

                    if username_str:

                        if username_str not in self.vip:

                            target_to_add = await self.webapi.get_users(username = username_str, limit=1)
                            if target_to_add.users:
                                target_username = target_to_add.users[0].username
                                await self.highrise.chat(f"@{target_username} has been added as VIP.")
                                self.vip.append(target_username)
                                self.save_vip()
                            else:
                                await self.highrise.chat(f"User not found with the username {username_str}.")
                        else:
                            await self.highrise.chat(f"@{username_str} is already a VIP.")
                            return
                    else:
                        await self.highrise.chat(f"User not found with the username {username_str}.")

                except Exception as e:
                    print(f"add_vip error: {e}")

            elif message.startswith("/removevip"):
                try:

                    parts = message.split(" ")
                    if len(parts) != 2:
                        await self.highrise.chat("Invalid command. Usage: /removevip @{username}")
                        return

                    target_username = parts[1]
                    if not target_username.startswith('@'):
                        await self.highrise.chat("Invalid username format. Use '@{username}'.")
                        return

                    username = target_username[1:]

                    if username in self.vip:
                        await self.highrise.chat(f"@{username} has been removed as VIP.")
                        self.vip.remove(username)
                        self.save_vip()
                    else:
                        await self.highrise.chat(f"User not found in VIP list.")
                except Exception as e:
                    print(f"An error occurred: {e}")


            elif message.lower().startswith("/teledown"):

                try:

                    parts = message.split(" ")
                    if len(parts) != 2:
                        await self.highrise.chat("Invalid command. Usage: /teledown @{username}.")
                        return

                    target_username = parts[1]
                    
                    if target > 91:
                        await self.highrise.chat(f"Invalid Emote.")
                        return
                    else:
                        emote_text, emote_time = await self.get_emote(target)
                        if emote_text and emote_time:

                            user_id = user.id
                            if user_id in self.emote_tasks:
                                self.emote_tasks[user_id].cancel()

                            task = asyncio.create_task(self.emote_loop(emote_text, emote_time, user_id))
                            self.emote_tasks[user_id] = task
                else:
                    await self.highrise.chat(f"Please provide a valid Emote number.")
                    return
            except Exception as e:
                print(f"An error occurred: {e}")

        elif message.startswith("/stop-emote"):
            # Stop the emote loop for the player
            try:
                if self.active_emote_loops[user.id]:
                    self.active_emote_loops[user.id] = False
                    await self.highrise.send_whisper(user.id, f"Emote loop for @{user.username} stopped.")
            except Exception as e:
                # Handle other exceptions
                print(f"Unexpected error: {e}")

    async def moderate_user(self, target_user, moderate_key, length=None):

        try:

            if moderate_key == "unban":
                target_to_unban = await self.webapi.get_users(username = target_user, limit=1)

                if target_to_unban.users:
                    target_user_id = target_to_unban.users[0].user_id
                else:
                    await self.highrise.chat(f"User with username {target_user} not found.")

                await self.highrise.moderate_room(target_user_id, moderate_key)
                await self.highrise.chat(f"@{target_user} has been successfuly unbanned.")
                return

            if target_user:

                target = await self.get_target_user_in_room(target_user)

                if target:

                    if moderate_key == "kick":
                        await self.highrise.moderate_room(target.id, moderate_key)
                        await self.highrise.chat(f"@{target.username} has been successfully kicked.")

                    elif moderate_key == "ban":
                        await self.highrise.moderate_room(target.id, moderate_key, length)
                        await self.highrise.chat(f"@{target.username} has been successfully banned for {length} seconds.")

                    elif moderate_key == "mute":
                        await self.highrise.moderate_room(target.id, moderate_key, length)
                        await self.highrise.chat(f"@{target.username} has been successfully muted for {length} seconds.")

                else:
                    await self.highrise.chat(f"Username {target_user} is invalid.")

        except Exception as e:
            print(f"moderate_user error: {e}")


    async def get_actual_pos(self, user_id):

        room_users = await self.highrise.get_room_users()

        for user, position in room_users.content:
            if user.id == user_id:
                return position

    async def pick_up_lines(self, number_of_times):

        try:

            for _ in range(number_of_times):

                users_in_room = await self.get_users_in_room()
                users_in_room_except_bot = [user for user in users_in_room if user.id != self.highrise.my_id]

                if self.plines:

                    if users_in_room:

                        target = random.choice(users_in_room_except_bot)

                        if target:

                            targetloc = await self.get_actual_pos(target.id)

                            if isinstance(targetloc, Position):

                                loc_final = Position(targetloc.x + 1, targetloc.y, targetloc.z)
                                if targetloc:

                                    await self.highrise.teleport(self.highrise.my_id, loc_final)
                                    await asyncio.sleep(1)
                                    targetloc = await self.get_actual_pos(target.id)
                                    loc_final = Position(targetloc.x + 2, targetloc.y, targetloc.z, facing="FrontLeft")
                                    await self.highrise.walk_to(loc_final)
                                    await asyncio.sleep(2)
                                    reacts = ('wave', 'heart', 'wink')
                                    ran_reacts = random.choice(reacts)
                                    ran_PUL = random.choice(self.pickuplines)
                                    await self.highrise.react(ran_reacts, target.id)
                                    await self.highrise.chat(f"@{target.username} {ran_PUL}")

                            else:
                                continue    
                else:
                    break

                await asyncio.sleep(5)

            await self.highrise.teleport(self.highrise.my_id, self.bot_pos)
            await self.highrise.chat(f"Pick-up lines stopped.")
            self.plines = False

        except Exception as e:
            await self.highrise.teleport(self.highrise.my_id, self.bot_pos)
            self.plines = False
            print(f"plines error: {e}")

    async def teleport_target_user_to_loc(self, target_username, loc):

        try:
            if target_username:
                target = await self.get_target_user_in_room(target_username)

                if target:

                    if loc:
                        await self.highrise.teleport(target.id, loc)
                        await self.highrise.chat(f"@{target.username} has been successfuly teleported.")
                    else:
                        await self.highrise.chat(f"Target location is not set.")

                else:
                    await self.highrise.chat(f"Username {target_username} is invalid.")
        except Exception as e:
            print(f"teleport_target_user: {e}")

    async def get_target_user_in_room(self, target_username):

        room_users = await self.highrise.get_room_users()
        target_user = next((user for user, _ in room_users.content if user.username == target_username), None)
        return target_user

    async def get_users_in_room(self):

        try:
            room_users = await self.highrise.get_room_users()

            if room_users.content:
                for user in room_users.content:
                    get_user = [user for user, _ in room_users.content]
                    return get_user
            else:
                return []
        except Exception as e:
            print(f"{e}")

    async def get_user_ids_in_room(self):

        try:
            room_users = await self.highrise.get_room_users()

            if 
                                return

                    # If not in any dance floor area
                    if user.id in self.dancer:
                        self.dancer.remove(user.id)
        except Exception as e:
            print(f"on_user_move error: {e}")

    async def create_dance_floor(self):

        # Assuming pos1 and pos2 are set as Position objects
        min_x = min(self.pos1.x, self.pos2.x)
        max_x = max(self.pos1.x, self.pos2.x)
        min_y = min(self.pos1.y, self.pos2.y)
        max_y = max(self.pos1.y, self.pos2.y)
        min_z = min(self.pos1.z, self.pos2.z)
        max_z = max(self.pos1.z, self.pos2.z)

        # Store the square area as a tuple and add it to on_dance_floor list
        dance_floor_pos = (min_x, max_x, min_y, max_y, min_z, max_z)
        self.on_dance_floor.append(dance_floor_pos)
        self.save_loc_data()


    def save_loc_data(self):

        loc_data = {
            'vip_position': {'x': self.vip_pos.x, 'y': self.vip_pos.y, 'z': self.vip_pos.z} if self.vip_pos else None,
            'bot_position': {'x': 

                