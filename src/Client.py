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
    print('quit (exits program)')

if __name__ == '__main__':
    username = input('Enter username: ')
    password = input('Enter password: ')
    if Lib.user_login(username):
        print('Login successfull')
    else:
        print('Incorrect credentials, program closing')
        sys.exit()


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


