package com.launchdarkly.featureflag.service;

import com.launchdarkly.featureflag.helper.UserValidationHelper;
import com.launchdarkly.featureflag.util.LDConstants;
import com.launchdarkly.featureflag.util.LDUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class LaunchDarklyUserService implements ILaunchDarklyUserService {

    @Autowired
    private UserValidationHelper userValidationHelper;

    @Override
    public String validateUserDetails(String username) {

        if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L, LDConstants.PW_ENABLE_USER_LOGIN_VALIDATION)) {
            if(userValidationHelper.isValidateUserDetails(username)){
                return "flag user name " + username;
            } else {
                return "Invalid username given " + username;
            }
        } else {
            return "else block";
        }
    }

    @Override
    public String getUserDetails(String userId) {

        if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L, LDConstants.PW_FIND_USER_DETAILS)) {
            return "User found for this userId";
        } else {
            return "Data not found for user ID: " + userId;
        }
    }
}
