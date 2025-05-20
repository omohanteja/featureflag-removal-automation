package com.launchdarkly.featureflag.helper;

import com.launchdarkly.featureflag.util.LDConstants;
import com.launchdarkly.featureflag.util.LDUtil;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

@Component
public class UserValidationHelper {

    public boolean isValidateUserDetails(String userName){
        if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L, LDConstants.PW_VALIDATE_USERNAME)) {
            if (!StringUtils.isEmpty(userName) && (userName.length() >= 4 && userName.length() <= 16)) {
                return true;
            }
            return false;
        } else {
            return true;
        }
    }
}
