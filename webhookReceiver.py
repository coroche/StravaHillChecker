try:
    import activityFunctions
    import sys

    hillFound = activityFunctions.processActivity(sys.argv[1])
    print('Activity:' + sys.argv[1] + ' processed')
    if hillFound:
        print('Description updated')
except Exception as e:
    print(e)
sys.stdout.flush()