package com.campusflow.domain.enums;

public enum ActivityStatus {
    DRAFT("draft"),
    PUBLISHED("published"),
    SIGNUP_OPEN("signup_open"),
    SIGNUP_CLOSED("signup_closed"),
    FINISHED("finished"),
    CANCELLED("cancelled");

    private final String code;

    ActivityStatus(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}
