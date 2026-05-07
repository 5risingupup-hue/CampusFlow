package com.campusflow.domain.enums;

public enum SignType {
    CODE("code"),
    QRCODE("qrcode");

    private final String code;

    SignType(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}
