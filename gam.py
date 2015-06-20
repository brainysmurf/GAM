#!/usr/bin/env python
#
# GAM 
#
# Copyright 2015, LLC All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

u"""GAM is a command line tool which allows Administrators to control their Google Apps domain and accounts.

With GAM you can programatically create users, turn on/off services for users like POP and Forwarding and much more.
For more information, see http://git.io/gam

"""
import sys, os, socket

from gamlib import *   # clean this up later

# Let click manage this
# reload(sys)  # why need this for setdefaultencoding?
# sys.setdefaultencoding(u'UTF-8')


try:
  if os.name == u'nt':
    sys.argv = win32_unicode_argv() # cleanup sys.argv on Windows
  doGAMCheckForUpdates()
  if sys.argv[1].lower() == u'batch':
    import shlex, subprocess
    python_cmd = [sys.executable.lower(),]
    if not getattr(sys, 'frozen', False): # we're not frozen
      python_cmd.append(os.path.realpath(sys.argv[0]))
    f = file(sys.argv[2], 'rb')
    items = list()
    for line in f:
      argv = shlex.split(line)
      if argv[0] in [u'#', u' ', u''] or len(argv) < 2:
        continue
      elif argv.pop(0).lower() not in [u'gam', u'commit-batch']:
        print u'Error: "%s" is not a valid gam command' % line
        continue
      items.append(python_cmd+argv)
    run_batch(items)
    sys.exit(0)
  elif sys.argv[1].lower() == 'csv':
    import subprocess
    python_cmd = [sys.executable.lower(),]
    if not getattr(sys, 'frozen', False): # we're not frozen
      python_cmd.append(os.path.realpath(sys.argv[0]))
    csv_filename = sys.argv[2]
    if csv_filename == u'-':
      import StringIO
      input_string = unicode(sys.stdin.read())
      f = StringIO.StringIO(input_string)
    else:
      f = file(csv_filename, 'rb')
    input_file = csv.DictReader(f)
    if sys.argv[3].lower() != 'gam':
      print 'Error: "gam csv <filename>" should be followed by a full GAM command...'
      sys.exit(3)
    argv_template = sys.argv[4:]
    items = list()
    for row in input_file:
      argv = list()
      for arg in argv_template:
        if arg[0] != '~':
          argv.append(arg)
        elif arg[1:] in row.keys():
          argv.append(row[arg[1:]])
        else:
          print 'Error: header "%s" not found in CSV headers of %s, giving up.' % (row.keys(), arg[1:])
          sys.exit(0)
      items.append(python_cmd+argv)
    run_batch(items)
    sys.exit(0)
  elif sys.argv[1].lower() == u'version':
    doGAMVersion()
    sys.exit(0)
  elif sys.argv[1].lower() == u'create':
    if sys.argv[2].lower() == u'user':
      doCreateUser()
    elif sys.argv[2].lower() == u'group':
      doCreateGroup()
    elif sys.argv[2].lower() in [u'nickname', u'alias']:
      doCreateAlias()
    elif sys.argv[2].lower() in [u'org', 'ou']:
      doCreateOrg()
    elif sys.argv[2].lower() == u'resource':
      doCreateResource()
    elif sys.argv[2].lower() in [u'verify', u'verification']:
      doSiteVerifyShow()
    elif sys.argv[2].lower() in [u'schema']:
      doCreateOrUpdateUserSchema()
    else:
      print u'Error: invalid argument to "gam create..."'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() == u'update':
    if sys.argv[2].lower() == u'user':
      doUpdateUser([sys.argv[3],])
    elif sys.argv[2].lower() == u'group':
      doUpdateGroup()
    elif sys.argv[2].lower() in [u'nickname', u'alias']:
      doUpdateAlias()
    elif sys.argv[2].lower() in [u'ou', u'org']:
      doUpdateOrg()
    elif sys.argv[2].lower() == u'resource':
      doUpdateResourceCalendar()
    elif sys.argv[2].lower() == u'domain':
      doUpdateDomain()
    elif sys.argv[2].lower() == u'cros':
      doUpdateCros()
    elif sys.argv[2].lower() == u'mobile':
      doUpdateMobile()
    elif sys.argv[2].lower() in [u'notification', u'notifications']:
      doUpdateNotification()
    elif sys.argv[2].lower() in [u'verify', u'verification']:
      doSiteVerifyAttempt()
    elif sys.argv[2].lower() in [u'schema', u'schemas']:
      doCreateOrUpdateUserSchema()
    else:
      showUsage()
      print u'Error: invalid argument to "gam update..."'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() == u'info':
    if sys.argv[2].lower() == u'user':
      doGetUserInfo()
    elif sys.argv[2].lower() == u'group':
      doGetGroupInfo()
    elif sys.argv[2].lower() in [u'nickname', u'alias']:
      doGetAliasInfo()
    elif sys.argv[2].lower() == u'domain':
      doGetDomainInfo()
    elif sys.argv[2].lower() in [u'org', u'ou']:
      doGetOrgInfo()
    elif sys.argv[2].lower() == u'resource':
      doGetResourceCalendarInfo()
    elif sys.argv[2].lower() == u'cros':
      doGetCrosInfo()
    elif sys.argv[2].lower() == u'mobile':
      doGetMobileInfo()
    elif sys.argv[2].lower() in [u'notifications', u'notification']:
      doGetNotifications()
    elif sys.argv[2].lower() in [u'verify', u'verification']:
      doGetSiteVerifications()
    elif sys.argv[2].lower() in [u'schema', u'schemas']:
      doGetUserSchema()
    else:
      print u'Error: invalid argument to "gam info..."'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() == u'delete':
    if sys.argv[2].lower() == u'user':
      doDeleteUser()
    elif sys.argv[2].lower() == u'group':
      doDeleteGroup()
    elif sys.argv[2].lower() in [u'nickname', u'alias']:
      doDeleteAlias()
    elif sys.argv[2].lower() == u'org':
      doDeleteOrg()
    elif sys.argv[2].lower() == u'resource':
      doDeleteResourceCalendar()
    elif sys.argv[2].lower() == u'mobile':
      doDeleteMobile()
    elif sys.argv[2].lower() in [u'notification', u'notifications']:
      doDeleteNotification()
    elif sys.argv[2].lower() in [u'verify', u'verification']:
      doDelSiteVerify()
    elif sys.argv[2].lower() in [u'schema', u'schemas']:
      doDelSchema()
    else:
      print u'Error: invalid argument to "gam delete"'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() == u'undelete':
    if sys.argv[2].lower() == u'user':
      doUndeleteUser()
    else:
      print u'Error: invalid argument to "gam undelete..."'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() == u'audit':
    if sys.argv[2].lower() == u'monitor':
      if sys.argv[3].lower() == u'create':
        doCreateMonitor()
      elif sys.argv[3].lower() == u'list':
        doShowMonitors()
      elif sys.argv[3].lower() == u'delete':
        doDeleteMonitor()
      else:
        print u'Error: invalid argument to "gam audit monitor..."'
        sys.exit(2)
    elif sys.argv[2].lower() == u'activity':
      if sys.argv[3].lower() == u'request':
        doRequestActivity()
      elif sys.argv[3].lower() == u'status':
        doStatusActivityRequests()
      elif sys.argv[3].lower() == u'download':
        doDownloadActivityRequest()
      elif sys.argv[3].lower() == u'delete':
        doDeleteActivityRequest()
      else:
        print u'Error: invalid argument to "gam audit activity..."'
        sys.exit(2)
    elif sys.argv[2].lower() == u'export':
      if sys.argv[3].lower() == u'status':
        doStatusExportRequests()
      elif sys.argv[3].lower() == u'watch':
        doWatchExportRequest()
      elif sys.argv[3].lower() == u'download':
        doDownloadExportRequest()
      elif sys.argv[3].lower() == u'request':
        doRequestExport()
      elif sys.argv[3].lower() == u'delete':
        doDeleteExport()
      else:
        print u'Error: invalid argument to "gam audit export..."'
        sys.exit(2)
    elif sys.argv[2].lower() == u'uploadkey':
      doUploadAuditKey()
    elif sys.argv[2].lower() == u'admin':
      doAdminAudit()
    else:
      print u'Error: invalid argument to "gam audit..."'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() == u'print':
    if sys.argv[2].lower() == u'users':
      doPrintUsers()
    elif sys.argv[2].lower() == u'nicknames' or sys.argv[2].lower() == u'aliases':
      doPrintAliases()
    elif sys.argv[2].lower() == u'groups':
      doPrintGroups()
    elif sys.argv[2].lower() in [u'group-members', u'groups-members']:
      doPrintGroupMembers()
    elif sys.argv[2].lower() in [u'orgs', u'ous']:
      doPrintOrgs()
    elif sys.argv[2].lower() == u'resources':
      doPrintResources()
    elif sys.argv[2].lower() == u'cros':
      doPrintCrosDevices()
    elif sys.argv[2].lower() == u'mobile':
      doPrintMobileDevices()
    elif sys.argv[2].lower() in [u'license',  u'licenses']:
      doPrintLicenses()
    elif sys.argv[2].lower() in [u'token', u'tokens']:
      doPrintTokens()
    elif sys.argv[2].lower() in [u'schema', u'schemas']:
      doPrintUserSchemas()
    else:
      print u'Error: invalid argument to "gam print..."'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() in [u'oauth', u'oauth2']:
    if sys.argv[2].lower() in [u'request', u'create']:
      doRequestOAuth()
    elif sys.argv[2].lower() == u'info':
      OAuthInfo()
    elif sys.argv[2].lower() in [u'delete', u'revoke']:
      doDeleteOAuth()
    elif sys.argv[2].lower() == u'select':
      doOAuthSelect()
    else:
      print u'Error: invalid argument to "gam oauth..."'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() == u'calendar':
    if sys.argv[3].lower() == u'showacl':
      doCalendarShowACL()
    elif sys.argv[3].lower() == u'add':
      doCalendarAddACL()
    elif sys.argv[3].lower() in [u'del', u'delete']:
      doCalendarDelACL()
    elif sys.argv[3].lower() == u'update':
      doCalendarUpdateACL()
    elif sys.argv[3].lower() == u'wipe':
      doCalendarWipeData()
    elif sys.argv[3].lower() == u'addevent':
      doCalendarAddEvent()
    else:
      print u'Error: invalid argument to "gam calendar..."'
      sys.exit(2)
    sys.exit(0)
  elif sys.argv[1].lower() == u'report':
    showReport()
    sys.exit(0)
  elif sys.argv[1].lower() == u'whatis':
    doWhatIs()
    sys.exit(0)
  users = getUsersToModify()
  command = sys.argv[3].lower()
  if command == u'print':
    for user in users:
      print user
  elif command == u'transfer':
    transferWhat = sys.argv[4].lower()
    if transferWhat == u'drive':
      transferDriveFiles(users)
    elif transferWhat == u'seccals':
      transferSecCals(users)
  elif command == u'show':
    readWhat = sys.argv[4].lower()
    if readWhat in [u'labels', u'label']:
      showLabels(users)
    elif readWhat == u'profile':
      showProfile(users)
    elif readWhat == u'calendars':
      showCalendars(users)
    elif readWhat == u'calsettings':
      showCalSettings(users)
    elif readWhat == u'drivesettings':
      showDriveSettings(users)
    elif readWhat == u'drivefileacl':
      showDriveFileACL(users)
    elif readWhat == u'filelist':
      showDriveFiles(users)
    elif readWhat == u'filetree':
      showDriveFileTree(users)
    elif readWhat == u'fileinfo':
      showDriveFileInfo(users)
    elif readWhat == u'sendas':
      showSendAs(users)
    elif readWhat == u'gmailprofile':
      showGmailProfile(users)
    elif readWhat in [u'sig', u'signature']:
      getSignature(users)
    elif readWhat == u'forward':
      getForward(users)
    elif readWhat in [u'pop', u'pop3']:
      getPop(users)
    elif readWhat in [u'imap', u'imap4']:
      getImap(users)
    elif readWhat == u'vacation':
      getVacation(users)
    elif readWhat in [u'delegate', u'delegates']:
      getDelegates(users)
    elif readWhat in [u'backupcode', u'backupcodes', u'verificationcodes']:
      doGetBackupCodes(users)
    elif readWhat in [u'asp', u'asps', u'applicationspecificpasswords']:
      doGetASPs(users)
    elif readWhat in [u'token', u'tokens', u'oauth', u'3lo']:
      doGetTokens(users)
    elif readWhat in [u'driveactivity']:
      doDriveActivity(users)
    else:
      print u'Error: invalid argument to "gam <users> show..."'
      sys.exit(2)
  elif command == u'delete' or command == u'del':
    delWhat = sys.argv[4].lower()
    if delWhat == u'delegate':
      deleteDelegate(users)
    elif delWhat == u'calendar':
      deleteCalendar(users)
    elif delWhat == u'label':
      doDeleteLabel(users)
    elif delWhat == u'photo':
      deletePhoto(users)
    elif delWhat == u'license':
      doLicense(users, u'delete')
    elif delWhat in [u'backupcode', u'backupcodes', u'verificationcodes']:
      doDelBackupCodes(users)
    elif delWhat in [u'asp', u'asps', u'applicationspecificpasswords']:
      doDelASP(users)
    elif delWhat in [u'token', u'tokens', u'oauth', u'3lo']:
      doDelTokens(users)
    elif delWhat in [u'group', u'groups']:
      doRemoveUsersGroups(users)
    elif delWhat in [u'alias', u'aliases']:
      doRemoveUsersAliases(users)
    elif delWhat in [u'emptydrivefolders']:
      deleteEmptyDriveFolders(users)
    elif delWhat in [u'drivefile']:
      deleteDriveFile(users)
    elif delWhat in [u'drivefileacl', u'drivefileacls']:
      delDriveFileACL(users)
    else:
      print u'Error: invalid argument to "gam <users> delete..."'
      sys.exit(2)
  elif command == u'add':
    addWhat = sys.argv[4].lower()
    if addWhat == u'calendar':
      addCalendar(users)
    elif addWhat == u'drivefile':
      createDriveFile(users)
    elif addWhat == u'license':
      doLicense(users, u'insert')
    elif addWhat in [u'drivefileacl', u'drivefileacls']:
      addDriveFileACL(users)
    elif addWhat in [u'label', u'labels']:
      doLabel(users)
    else:
      print u'Error: invalid argument to "gam <users> add..."'
      sys.exit(2)
  elif command == u'update':
    if sys.argv[4].lower() == u'calendar':
      updateCalendar(users)
    elif sys.argv[4].lower() == u'calattendees':
      changeCalendarAttendees(users)
    elif sys.argv[4].lower() == u'photo':
      doPhoto(users)
    elif sys.argv[4].lower() == u'license':
      doLicense(users, u'patch')
    elif sys.argv[4].lower() == u'user':
      doUpdateUser(users)
    elif sys.argv[4].lower() in [u'backupcode', u'backupcodes', u'verificationcodes']:
      doGenBackupCodes(users)
    elif sys.argv[4].lower() in [u'drivefile']:
      doUpdateDriveFile(users)
    elif sys.argv[4].lower() in [u'drivefileacls', u'drivefileacl']:
      updateDriveFileACL(users)
    elif sys.argv[4].lower() in [u'label', u'labels']:
      renameLabels(users)
    elif sys.argv[4].lower() in [u'labelsettings']:
      updateLabels(users)
    else:
      print u'Error: invalid argument to "gam <users> update..."'
      sys.exit(2)
  elif command in [u'deprov', u'deprovision']:
    doDeprovUser(users)
  elif command == u'get':
    if sys.argv[4].lower() == u'photo':
      getPhoto(users)
    elif sys.argv[4].lower() == u'drivefile':
      downloadDriveFile(users)
  elif command == u'profile':
    doProfile(users)
  elif command == u'imap':
    doImap(users)
  elif command in [u'pop', u'pop3']:
    doPop(users)
  elif command == u'sendas':
    doSendAs(users)
  elif command == u'language':
    doLanguage(users)
  elif command in [u'utf', u'utf8', u'utf-8', u'unicode']:
    doUTF(users)
  elif command == u'pagesize':
    doPageSize(users)
  elif command == u'shortcuts':
    doShortCuts(users)
  elif command == u'arrows':
    doArrows(users)
  elif command == u'snippets':
    doSnippets(users)
  elif command == u'label':
    doLabel(users)
  elif command == u'filter':
    doFilter(users)
  elif command == u'forward':
    doForward(users)
  elif command in [u'sig', u'signature']:
    doSignature(users)
  elif command == u'vacation':
    doVacation(users)
  elif command == u'webclips':
    doWebClips(users)
  elif command in [u'delegate', u'delegates']:
    doDelegates(users)
  else:
    print u'Error: %s is not a valid gam command' % command
    sys.exit(2)
except IndexError:
  showUsage()
  sys.exit(2)
except KeyboardInterrupt:
  sys.exit(50)
except socket.error, e:
  print u'\nError: %s' % e
  sys.exit(3)
except MemoryError:
  print u'Error: GAM has run out of memory. If this is a large Google Apps instance, you should use a 64-bit version of GAM on Windows or a 64-bit version of Python on other systems.'
  sys.exit(99)
