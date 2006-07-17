source ${O2O_SETUP_DIR}/general-db-setup.sh

SUBDETECTOR_OFFLINE_USER=CMS_COND_DT # uppercase for connect string
SUBDETECTOR_OFFLINE_PASSWORD=__CHANGE_ME__
SUBDETECTOR_ONLINE_USER=drifttube
SUBDETECTOR_ONLINE_PASSWORD=__CHANGE_ME__

OFFLINE_CONNECT=oracle://${OFFLINE_DB}/${SUBDETECTOR_OFFLINE_USER}
export CORAL_AUTH_USER=$SUBDETECTOR_OFFLINE_USER
export CORAL_AUTH_PASSWORD=$SUBDETECTOR_OFFLINE_PASSWORD
