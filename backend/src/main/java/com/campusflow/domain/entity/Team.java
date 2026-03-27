package com.campusflow.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("team")
public class Team extends BaseEntity {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long activityId;

    private String teamName;

    private Long leaderId;

    private String slogan;

    private String description;

    private String inviteCode;

    private String status;
}
