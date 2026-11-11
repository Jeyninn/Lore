package com.lore.backend.dto.request;

import jakarta.validation.constraints.*;

public class UserRequest {
    @NotBlank(message = "Username cannot be empty")
    private String username;

    @NotBlank(message = "Email cannot be empty")
    @Email(message = "Please provide a valid email")
    private String email;

    @NotBlank(message = "Password cannot be empty")
    @jakarta.validation.constraints.Size(
            min = 8,
            message = "Password must contain at least 8 characters"
    )
    private String password;
    public UserRequest() {}

    public String getUsername() {
        return username;
    }

    public String getEmail() {
        return email;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setEmail(String email) {
        this.email = email;
    }
    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}