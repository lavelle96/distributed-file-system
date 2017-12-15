import Lib
import sys


def print_help():
    print('available commands: ')
    print('show (shows files available)')
    print('help (displays available commands)')
    print('read <file name> (reads a the file if available)')
    print('write <file name> (reads file with write privileges)')
    print('delete <file name> (deletes file)')
    print('create <file name> (creates empty file)')
    print('quit (exits program)\n')

def print_admin_help():

    print('available commands (admin): ')
    print('show (shows files available)')
    print('help (displays available commands)')
    print('read <file name> (reads a the file if available)')
    print('write <file name> (reads file with write privileges)')
    print('delete <file name> (deletes file)')
    print('create <file name> (creates empty file)')
    print('add_user (adds user to database)')
    print('show_users (shows existing users)')
    print('quit (exits program)\n')

if __name__ == '__main__':
    username = input('Enter username: ')
    password = input('Enter password: ')
    admin = Lib.admin_login(username, password)
    if Lib.user_login(username, password):
        print('Login successfull')
    else:
        print('Incorrect credentials, program closing')
        sys.exit()

    if admin:
        print_admin_help()
        while(1):
            admin_username = username
            admin_password = password
            #Display protocol to the user
            user_input = input('Enter command or the file system\n')
            user_input = user_input.split(" ")
            
            command = user_input[0]
            #Read 
            if command == 'show':
                #Show available files
                Lib.show()
                pass
            elif command == 'help':
                #Show possible commands and syntax
                print_admin_help()
                pass
            elif command == 'read':
                #Read file
                file_name = user_input[1]
                Lib.read_file(file_name)
                pass
            elif command == 'write':
                #Read with write privileges
                file_name = user_input[1]
                Lib.write_file(file_name)
                pass
            elif command == 'create':
                #Create file
                file_name = user_input[1]
                Lib.create_file(file_name)
                pass
            elif command == 'delete':
                #Delete file
                file_name = user_input[1]
                Lib.delete_file(file_name)
                pass
            elif command == 'add_user':
                new_username = input('Enter new username: ')
                new_password = input('Enter new password: ')
                new_privilege = input('Enter new privilege: ')
                if Lib.add_user(admin_username, admin_password, new_username, new_password, new_privilege):
                    print('Success!')
                else:
                    print('Unable to perform command')
            elif command == 'show_users':
                Lib.show_users(admin_username, admin_password)
            elif command == 'quit':
                break
            else:
                print('Incorrect syntax in command')
            print('\n')
    else:  
        print_help()
        while(1):

            #Display protocol to the user
            user_input = input('Enter command or the file system\n')
            user_input = user_input.split(" ")
            
            command = user_input[0]
            #Read 
            if command == 'show':
                #Show available files
                Lib.show()
                pass
            elif command == 'help':
                #Show possible commands and syntax
                print_help()
                pass
            elif command == 'read':
                #Read file
                file_name = user_input[1]
                Lib.read_file(file_name)
                pass
            elif command == 'write':
                #Read with write privileges
                file_name = user_input[1]
                Lib.write_file(file_name)
                pass
            elif command == 'create':
                #Create file
                file_name = user_input[1]
                Lib.create_file(file_name)
                pass
            elif command == 'delete':
                #Delete file
                file_name = user_input[1]
                Lib.delete_file(file_name)
                pass
            elif command == 'quit':
                break
            else:
                print('Incorrect syntax in command')
            print('\n')


