package com.campusflow.domain.enums;

public enum RoleName {
    STUDENT("student"),
    CAPTAIN("captain"),
    ORGANIZER("organizer"),
    ADMIN("admin");

    private final String code;

    RoleName(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}
