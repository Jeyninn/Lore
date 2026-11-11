package com.lore.backend.controller;

import com.lore.backend.dto.request.LoginRequest;
import com.lore.backend.dto.request.UserRequest;
import com.lore.backend.dto.response.LoginResponse;
import com.lore.backend.dto.response.UserResponse;
import com.lore.backend.entity.User;
import com.lore.backend.service.LoreService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import com.lore.backend.dto.response.UserResponse;
@RestController
@RequestMapping("/api/v1/lore")
public class LoreController {

    private final LoreService loreService;

    public LoreController(LoreService loreService) {
        this.loreService = loreService;
    }

    @PostMapping("/users")
    public UserResponse createUser(@Valid @RequestBody UserRequest request) {
        return loreService.createUser(request);
    }

    @PostMapping("/login")
    public LoginResponse login(@Valid @RequestBody LoginRequest request){
        return loreService.login(request);
    }
    @GetMapping("/me")
    public UserResponse getCurrentUser(
            @AuthenticationPrincipal String email) {

        return loreService.getCurrentUser(email);
    }
}