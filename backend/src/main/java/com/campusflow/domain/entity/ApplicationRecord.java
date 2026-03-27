package com.campusflow.domain.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("application_record")
public class ApplicationRecord extends BaseEntity {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long activityId;

    private Long teamId;

    private Long applicantId;

    private String type;

    private String status;

    private String reason;

    private Long reviewedBy;

    private LocalDateTime reviewedAt;

    private String reviewComment;
}
