package com.campusflow.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("activity")
public class Activity extends BaseEntity {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String title;

    private String coverUrl;

    private String description;

    private Long organizerId;

    private String type;

    private String location;

    private LocalDateTime startTime;

    private LocalDateTime endTime;

    private LocalDateTime signupDeadline;

    private Boolean requireTeam;

    private Integer minTeamSize;

    private Integer maxTeamSize;

    private String status;

    private String tags;

    private String signCode;

    private LocalDateTime signStartTime;

    private LocalDateTime signEndTime;

    private String resultSummary;
}
