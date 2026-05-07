package com.campusflow.domain.enums;

public enum NotificationType {
    REVIEW_RESULT("review_result"),
    ACTIVITY_REMINDER("activity_reminder"),
    SYSTEM("system"),
    TEAM_APPLY("team_apply"),
    ANNOUNCEMENT("announcement");

    private final String code;

    NotificationType(String code) {
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}
