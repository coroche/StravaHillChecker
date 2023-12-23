try:
    import sys
    from library import activityFunctions
except Exception as e:
    print(e)
    sys.stdout.flush()

def handleWebhook(activityID):
    
    try:
        hillFound, _ = activityFunctions.processActivity(activityID)
        print('Activity:' + str(activityID) + ' processed')
        if hillFound:
            print('Description updated')
    except Exception as e:
        print(e)
    sys.stdout.flush()

if __name__ == "__main__":
    handleWebhook(sys.argv[1])