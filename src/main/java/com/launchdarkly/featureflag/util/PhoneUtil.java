package com.launchdarkly.featureflag.util;

import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.apache.commons.lang3.StringUtils;

public class PhoneUtil {

    private static final char[] PHONE_NUMBER_VALID_CHARS = new char[]{'0', '1','2','3','4','5','6','7','8','9','0','(',')','-','+',' '};
    public static final String TEXT_MESSAGE_PHONE_NUMBER_PATTERN = "\\+\\d+";
    public static final String NON_DIGIT_CHAR_REGEX = "\\D";
    public static final String MOBILE_NUMBER_USA_PREFIX = "1";
    public static final String EMPTY = "";
    public static final String PLUS = "+";

    public static boolean isE164Format(String phoneNumber) {
        return (!StringUtils.isBlank(phoneNumber) && phoneNumber.matches(TEXT_MESSAGE_PHONE_NUMBER_PATTERN));
    }

    public static boolean containsOnlyValidCharacters(String phoneNumber) {
        return StringUtils.containsOnly(phoneNumber, PHONE_NUMBER_VALID_CHARS);
    }

    public static String getPhoneNumberInE164Format(String phoneNumber) {
        if (StringUtils.isBlank(phoneNumber)) {
            return EMPTY;
        }
        if (isE164Format(phoneNumber)) {
            return phoneNumber;
        }

        String phone = phoneNumber.replaceAll(NON_DIGIT_CHAR_REGEX, EMPTY);
        if (phone.length() == 11 && phone.startsWith(MOBILE_NUMBER_USA_PREFIX)) {
            return StringUtils.join(PLUS, phone);
        }
        if (phone.length() == 10) {
            return StringUtils.join(PLUS, MOBILE_NUMBER_USA_PREFIX, phone);
        }

        return EMPTY;
    }
    public static boolean containsOnlyValidCharacters(String phoneNumber,char[] validCharacters){
        return StringUtils.containsOnly(phoneNumber,validCharacters);
    }

    public static boolean validatePhoneNumber(String phoneNumber){
        Pattern pattern = Pattern.compile("[\\+]?[0-9]{10,16}");
        Matcher m = pattern.matcher(phoneNumber);
        return m.matches();
    }


}
