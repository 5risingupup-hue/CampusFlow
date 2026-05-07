package com.campusflow.domain.enums;

public enum TeamStatus {
    FORMING("forming"),
    SUBMITTED("submitted"),
    APPROVED("approved"),
    REJECTED("rejected"),
    DISBANDED("disbanded");

    private final String code;

    TeamStatus(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}
