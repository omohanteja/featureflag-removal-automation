package com.launchdarkly.featureflag.service;

public interface ILaunchDarklyUserService {

    String validateUserDetails(String username);

    String getUserDetails(String username);
}
