package com.lore.backend.dto.response;

public class LoginResponse {

    private String message;
    private Long userId;
    private String username;
    private String token;

    public LoginResponse(
            String message,
            Long userId,
            String username,
            String token) {

        this.message = message;
        this.userId = userId;
        this.username = username;
        this.token = token;
    }
    public String getToken() {
        return token;
    }
    public String getMessage() {
        return message;
    }

    public Long getUserId() {
        return userId;
    }

    public String getUsername() {
        return username;
    }
}