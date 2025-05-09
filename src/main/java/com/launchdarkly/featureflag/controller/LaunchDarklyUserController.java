package com.launchdarkly.featureflag.controller;

import com.launchdarkly.featureflag.service.ILaunchDarklyUserService;
import com.launchdarkly.featureflag.util.LDConstants;
import com.launchdarkly.featureflag.util.LDUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LaunchDarklyUserController {

    @Autowired
    ILaunchDarklyUserService launchDarklyUserService;

    @GetMapping("/login")
    public String login(@RequestParam(required = false) String username, @RequestParam(required = false) String password) {

        if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L,LDConstants.PW_ENABLE_USER_LOGIN_VALIDATION)){
            if (username == null || username.isEmpty()) {
                return "Username is required!";
            }
            if (password != null && !password.isEmpty()) {
                return "User " + username + " logged in successfully with password!";
            }
            return launchDarklyUserService.getUserDetail(username);
        } else {
            return "Welcome user without validation ";
        }
    }

    @GetMapping("/getUserData")
    public String getUserData(@RequestParam String userId) {
        if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L,LDConstants.PW_ENABLE_USER_LOGIN_VALIDATION)) {
            return "Feature flag validation !!!";
        }

        return "Data for user ID: " + userId;
    }

}
