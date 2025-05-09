package com.launchdarkly.featureflag.service;

import com.launchdarkly.featureflag.util.LDConstants;
import com.launchdarkly.featureflag.util.LDUtil;
import org.springframework.stereotype.Service;

@Service
public class LaunchDarklyUserService implements ILaunchDarklyUserService {

    @Override
    public String getUserDetail(String username) {

        if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L, LDConstants.PW_ENABLE_USER_LOGIN_VALIDATION)) {
            return "flag user name " + username;
        } else {
            return "else block";
        }
    }
}
