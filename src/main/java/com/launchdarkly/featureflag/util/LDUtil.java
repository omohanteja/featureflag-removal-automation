package com.launchdarkly.featureflag.util;

import org.springframework.util.CollectionUtils;

import java.io.Serializable;
import java.util.Arrays;
import java.util.List;

public class LDUtil implements Serializable {

    public static boolean getFlagStatusBySystemIdDefaultFalse(Long systemId, String flagName) {

        List<String> trueEnabledFlagList = Arrays.asList(LDConstants.PW_CONTENT_USERNAME_RESTRICTION
        );

        if(!CollectionUtils.isEmpty(trueEnabledFlagList)) {
            if (trueEnabledFlagList.contains(flagName)) {
                return true;
            }
        }

        List<String> falseEnabledFlagList = Arrays.asList();

        if(!CollectionUtils.isEmpty(falseEnabledFlagList)) {
            if (falseEnabledFlagList.contains(flagName)) {
                return false;
            }
        }
        return false;
    }
}
