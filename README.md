# Processmaker
The following repository contains various resourceful python scripts to perform  

### Script name: ```processmaker_push_case.py```

* Description: Currently we use processmaker to submit events. The following python program pushes the case
to the next step in processmaker workflow right before 7 days of the event start date. This notify the users that the event is close by
and no more changes can be made.

Requirement: The following script will require a third party plugin called extrarest to be installed in processmaker. The plugin can be
download from the following link:
    https://github.com/amosbatto/pmcommunity/tree/master/extraRest
    
    
### Script Name: ```processmaker_download_output_doc.py```

* Description: The following code snippet will download the case passed as an argument to the function downloadSingleDoc. 
