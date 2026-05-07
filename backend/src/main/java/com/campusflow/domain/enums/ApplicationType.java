package com.campusflow.domain.enums;

public enum ApplicationType {
    JOIN_TEAM("join_team"),
    SIGNUP_TEAM("signup_team");

    private final String code;

    ApplicationType(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}
