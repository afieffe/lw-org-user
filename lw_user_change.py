import os, argparse, json
import logging
from laceworksdk import LaceworkClient
import concurrent.futures


GROUPS =  { 'admin' : 'LACEWORK_USER_GROUP_ADMIN' , 'power' : 'LACEWORK_USER_GROUP_POWER_USER' , 'read-only' : 'LACEWORK_USER_GROUP_READ_ONLY_USER'}


def get_account_list(lw_client,account_list):
    if 'all' in account_list:
        profile=lw_client.user_profile.get()
        sub_accounts=[]
        if profile:
            data=profile.get('data', None)
            for sub_account in  data[0]['accounts']:
                if sub_account['accountName'] not in sub_accounts:
                    sub_accounts.append(sub_account['accountName'])

    else:
        sub_accounts = account_list
    return sub_accounts

def get_guid_list(lw_client,user_list):
    guids = []
    pl = lw_client.team_users.get()
    #print(json.dumps(pl['data'],indent=4))
    for user in pl['data']:
        if 'email' in user.keys() and user['email'] in user_list:
            if user['orgAccess'] == 'ORG_ADMIN':
                print('Cannot manage ' + user['email'] + ' at account level')
            else:
                guids.append(user['userGuid'])

    return guids




def main(args):
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    try:
        lw_client = LaceworkClient(
            account=args.account,
            subaccount=args.subaccount,
            api_key=args.api_key,
            api_secret=args.api_secret,
            profile=args.profile
        )
    except Exception:
        raise

    sub_accounts=get_account_list(lw_client,args.sub_accounts)
    for sub_account in sub_accounts:
        print('Processing sub_account:' + sub_account )
        lw_client.set_subaccount(sub_account)
        guids = get_guid_list(lw_client,args.users)
        if len(guids) > 0:
            if len(args.add) > 0:
                for group in args.add:
                    lw_client.user_groups.add_users(GROUPS[group], guids)
            if len(args.remove) > 0:
                for group in args.add:
                    lw_client.user_groups.remove_users(GROUPS[group], guids)


if __name__ == '__main__':
    # Set up an argument parser
    parser = argparse.ArgumentParser(
        description=''
    )
    parser.add_argument(
        '--account',
        default=os.environ.get('LW_ACCOUNT', None),
        help='The Lacework account to use'
    )
    parser.add_argument(
        '--subaccount',
        default=os.environ.get('LW_SUBACCOUNT', None),
        help='The Lacework sub-account to use'
    )
    parser.add_argument(
        '--api-key',
        dest='api_key',
        default=os.environ.get('LW_API_KEY', None),
        help='The Lacework API key to use'
    )
    parser.add_argument(
        '--api-secret',
        dest='api_secret',
        default=os.environ.get('LW_API_SECRET', None),
        help='The Lacework API secret to use'
    )

    parser.add_argument(
        '-p', '--profile',
        default=os.environ.get('LW_PROFILE', None),
        help='The Lacework CLI profile to use'
    )
    parser.add_argument(
        '--users',
        default=[],
        nargs='+',
        help='List of user to update'
    )
    parser.add_argument(
        '-s','--sub-accounts',
        default=['all'],
        nargs='*',
        help='The sub-account where to change the user profile - all to change on all sub-accounts'
    )
    parser.add_argument(
        '-a','--add',
        choices=['admin', 'power', 'read-only'],
        default='read-only',
        nargs='*',
        help='The account type to set admin, power or read-only'
    )
    parser.add_argument(
        '-r','--remove',
        choices=['admin', 'power', 'read-only'],
        default='read-only',
        nargs='*',
        help='The group to remove, power or read-only'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=os.environ.get('LW_DEBUG', False),
        help='Enable debug logging'
    )

    args = parser.parse_args()


    main(args)
