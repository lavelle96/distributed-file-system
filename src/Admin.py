import Lib
import sys



def print_help():
    print('Available commands: ')
    print('add_user (adds user to database)')
    print('show_users (shows existing users)')
    print('quit (quits program)')
    print('help (shows available commands)\n')

if __name__ == '__main__':

    admin_username = input('Enter username: ')
    admin_password = input('Enter password: ')

    valid = Lib.admin_login(admin_username, admin_password)
    if not valid:
        print('Login unsuccessfull, no admin access')
        sys.exit()
    print('Login successfull\n')
    print_help()
    while(1):
        command = input('\nEnter command: ')
        if command == 'add_user':
            new_username = input('Enter new username: ')
            new_password = input('Enter new password: ')
            new_privilege = input('Enter new privilege: ')
            if Lib.add_user(admin_username, admin_password, new_username, new_password, new_privilege):
                print('Success!')
            else:
                print('Unable to perform command')
        elif command == 'show_users':
            Lib.show_users(admin_username, admin_password)
            
            
        elif command == 'help':
            print_help()
        elif command == 'quit':
            sys.exit()
        else:
            print('invalid syntax')