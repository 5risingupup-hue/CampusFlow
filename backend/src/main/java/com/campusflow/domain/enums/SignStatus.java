package com.campusflow.domain.enums;

public enum SignStatus {
    UNSIGNED("unsigned"),
    SIGNED("signed"),
    EXPIRED("expired");

    private final String code;

    SignStatus(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}
