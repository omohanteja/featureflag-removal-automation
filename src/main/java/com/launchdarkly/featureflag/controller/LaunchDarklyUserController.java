package com.launchdarkly.featureflag.controller;

import com.launchdarkly.featureflag.service.ILaunchDarklyUserService;
import com.launchdarkly.featureflag.util.LDConstants;
import com.launchdarkly.featureflag.util.LDUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

@RestController
public class LaunchDarklyUserController {

    @Autowired
    private ILaunchDarklyUserService launchDarklyUserService;

    @GetMapping("/login")
    public String login(@RequestParam(required = false) String username, @RequestParam(required = false) String password) {

        if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L,LDConstants.PW_ENABLE_USER_LOGIN_VALIDATION)){
            if (username == null || username.isEmpty()) {
                return "Username is required!";
            }
            if (password == null || password.isEmpty()) {
                return "Password is required! for login";
            }
            if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L,LDConstants.PW_FIND_USER_DETAILS)) {
                return launchDarklyUserService.getUserDetails(username);
            }
            return launchDarklyUserService.validateUserDetails(username);
        } else {
            return "Welcome user without validation ";
        }
    }

    @GetMapping("/getUserData")
    public String getUserData(@RequestParam String userId) {
        if(LDUtil.getFlagStatusBySystemIdDefaultFalse(0L,LDConstants.PW_FIND_USER_DETAILS)) {
            return launchDarklyUserService.getUserDetails(userId);
        }
        Optional<String> userData = Optional.ofNullable(launchDarklyUserService.getUserDetails(userId));
        return userData.get();
    }

}
