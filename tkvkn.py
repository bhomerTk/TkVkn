#!/usr/bin/env python3

# ============================================================================ #
# TkVkn.py                                                                     #
#---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---
#   source: https://github.com/realitix/vulkan
#           Apache License

#   Modifications to use the above code in tkinter are marked with #wbh.


# Python ---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---
import  ctypes
import  os
import  sys


# tkinter --+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---
import  tkinter     as tk


# PyPi -+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---
from    sdl2        import *
from    vulkan      import *


# My Files -+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---


#---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---
debug = True


#---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---
class TkVkn:
    def __init__ (self, parent):
        print ("TkVkn.__init__ ()", flush = True)                               #tbr
        self.parent = parent

        self.canvas  = tk.Frame (self.parent)    # frame to embed sdl2 window   #wbh
        self.canvas.update ()                                                   #wbh

        self.initWindow ()
        self.create_instance ()
        self.setup_debug_messenger ()
        self.create_surface ()
        self.select_physical_device ()
        self.select_queue_family ()
        self.create_logical_device_and_queues ()
        self.create_swapchain ()
        self.load_spirv_shaders ()
        self.create_render_pass ()
        self.create_graphic_pipeline ()
        self.create_framebuffers ()
        self.create_command_pools ()
        self.create_command_buffers ()
        self.create_semaphore ()
        self.poll ()                                                            #wbh


    def create_command_buffers (self):
        command_buffers_create = VkCommandBufferAllocateInfo (
            sType              = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            commandPool        = self.command_pool,
            level              = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            commandBufferCount = len (self.framebuffers))

        command_buffers = vkAllocateCommandBuffers (self.logical_device, command_buffers_create)

        # Record command buffer
        for k, command_buffer in enumerate (command_buffers):
            command_buffer_begin_create = VkCommandBufferBeginInfo (
                sType            = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
                flags            = VK_COMMAND_BUFFER_USAGE_SIMULTANEOUS_USE_BIT,
                pInheritanceInfo = None)

            vkBeginCommandBuffer (command_buffer, command_buffer_begin_create)

            # Create render pass
            render_area = VkRect2D (offset = VkOffset2D (x = 0, y = 0), extent = self.extent)
            color       = VkClearColorValue (float32 = [0, 1, 0, 1])
            clear_value = VkClearValue (color = color)

            render_pass_begin_create_info = VkRenderPassBeginInfo (
                sType           = VK_STRUCTURE_TYPE_RENDER_PASS_BEGIN_INFO,
                renderPass      = self.render_pass,
                framebuffer     = self.framebuffers[k],
                renderArea      = render_area,
                clearValueCount = 1,
                pClearValues    = [clear_value])

            vkCmdBeginRenderPass (command_buffer, render_pass_begin_create_info, VK_SUBPASS_CONTENTS_INLINE)

        #   Bing pipeline
            vkCmdBindPipeline (command_buffer, VK_PIPELINE_BIND_POINT_GRAPHICS, self.pipeline)

        #   Draw
            vkCmdDraw (command_buffer, 3, 1, 0, 0)

        #   End
            vkCmdEndRenderPass (command_buffer)
            vkEndCommandBuffer (command_buffer)

        self.command_buffers = command_buffers


    def create_command_pools (self):
        command_pool_create_info = VkCommandPoolCreateInfo (
            sType            = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            queueFamilyIndex = self.queue_graphic_index,
            flags            = 0)

        self.command_pool = vkCreateCommandPool (self.logical_device, command_pool_create_info, None)


    def create_framebuffers (self):
        framebuffers = []
        for image in self.image_views:
            attachments = [image]
            framebuffer_create_info = VkFramebufferCreateInfo (
                sType           = VK_STRUCTURE_TYPE_FRAMEBUFFER_CREATE_INFO,
                flags           = 0,
                renderPass      = self.render_pass,
                attachmentCount = len (attachments),
                pAttachments    = attachments,
                width           = self.extent.width,
                height          = self.extent.height,
                layers          = 1)

            framebuffers.append (vkCreateFramebuffer (self.logical_device, framebuffer_create_info, None))

        self.framebuffers = framebuffers


    def create_graphic_pipeline (self):
        vertex_input_create = VkPipelineVertexInputStateCreateInfo (
            sType                           = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
            flags                           = 0,
            vertexBindingDescriptionCount   = 0,
            pVertexBindingDescriptions      = None,
            vertexAttributeDescriptionCount = 0,
            pVertexAttributeDescriptions    = None)

        input_assembly_create = VkPipelineInputAssemblyStateCreateInfo (
            sType                  = VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
            flags                  = 0,
            topology               = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST,
            primitiveRestartEnable = VK_FALSE)

        viewport = VkViewport (
            x = 0.,
            y = 0.,
            width  = float (self.extent.width),
            height = float (self.extent.height),
            minDepth = 0.,
            maxDepth = 1.)

        scissor_offset = VkOffset2D (x = 0, y = 0)
        scissor = VkRect2D (offset = scissor_offset, extent = self.extent)

        viewport_state_create = VkPipelineViewportStateCreateInfo (
            sType         = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
            flags         = 0,
            viewportCount = 1,
            pViewports    = [viewport],
            scissorCount  = 1,
            pScissors     = [scissor])

        rasterizer_create = VkPipelineRasterizationStateCreateInfo (
            sType                   = VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
            flags                   = 0,
            depthClampEnable        = VK_FALSE,
            rasterizerDiscardEnable = VK_FALSE,
            polygonMode             = VK_POLYGON_MODE_FILL,
            lineWidth               = 1,
            cullMode                = VK_CULL_MODE_BACK_BIT,
            frontFace               = VK_FRONT_FACE_CLOCKWISE,
            depthBiasEnable         = VK_FALSE,
            depthBiasConstantFactor = 0.,
            depthBiasClamp          = 0.,
            depthBiasSlopeFactor    = 0.)

        multisample_create = VkPipelineMultisampleStateCreateInfo (
            sType                 = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
            flags                 = 0,
            sampleShadingEnable   = VK_FALSE,
            rasterizationSamples  = VK_SAMPLE_COUNT_1_BIT,
            minSampleShading      = 1,
            pSampleMask           = None,
            alphaToCoverageEnable = VK_FALSE,
            alphaToOneEnable      = VK_FALSE)

        color_blend_attachement = VkPipelineColorBlendAttachmentState (
            colorWriteMask      = VK_COLOR_COMPONENT_R_BIT | VK_COLOR_COMPONENT_G_BIT | VK_COLOR_COMPONENT_B_BIT | VK_COLOR_COMPONENT_A_BIT,
            blendEnable         = VK_FALSE,
            srcColorBlendFactor = VK_BLEND_FACTOR_ONE,
            dstColorBlendFactor = VK_BLEND_FACTOR_ZERO,
            colorBlendOp        = VK_BLEND_OP_ADD,
            srcAlphaBlendFactor = VK_BLEND_FACTOR_ONE,
            dstAlphaBlendFactor = VK_BLEND_FACTOR_ZERO,
            alphaBlendOp        = VK_BLEND_OP_ADD)

        color_blend_create = VkPipelineColorBlendStateCreateInfo (
            sType           = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
            flags           = 0,
            logicOpEnable   = VK_FALSE,
            logicOp         = VK_LOGIC_OP_COPY,
            attachmentCount = 1,
            pAttachments    = [color_blend_attachement],
            blendConstants  = [0, 0, 0, 0])

        push_constant_ranges = VkPushConstantRange (
            stageFlags = 0,
            offset     = 0,
            size       = 0)

        pipeline_layout_create_info = VkPipelineLayoutCreateInfo (
            sType                  = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
            flags                  = 0,
            setLayoutCount         = 0,
            pSetLayouts            = None,
            pushConstantRangeCount = 0,
            pPushConstantRanges    = [push_constant_ranges])

        pipeline_layout = vkCreatePipelineLayout (self.logical_device, pipeline_layout_create_info, None)

        # Finally create graphic pipeline
        pipeline_create_info = VkGraphicsPipelineCreateInfo (
            sType               = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
            flags               = 0,
            stageCount          = 2,
            pStages             = [self.vert_stage_create, self.frag_stage_create],
            pVertexInputState   = vertex_input_create,
            pInputAssemblyState = input_assembly_create,
            pTessellationState  = None,
            pViewportState      = viewport_state_create,
            pRasterizationState = rasterizer_create,
            pMultisampleState   = multisample_create,
            pDepthStencilState  = None,
            pColorBlendState    = color_blend_create,
            pDynamicState       = None,
            layout              = pipeline_layout,
            renderPass          = self.render_pass,
            subpass             = 0,
            basePipelineHandle  = None,
            basePipelineIndex   = -1)

        pipelines = vkCreateGraphicsPipelines (self.logical_device, None, 1, [pipeline_create_info], None)
        self.pipeline = pipelines[0]
        self.pipeline_layout = pipeline_layout


    def create_instance (self):
        appInfo = VkApplicationInfo (
            sType              = VK_STRUCTURE_TYPE_APPLICATION_INFO,
            pApplicationName   = "TkVulkan",
            applicationVersion = VK_MAKE_VERSION (1, 0, 0),
            pEngineName        = "No Engine",
            engineVersion      = VK_MAKE_VERSION (1, 0, 0),
            apiVersion         = VK_API_VERSION_1_0)

        layers = vkEnumerateInstanceLayerProperties ()
        layers = [l.layerName for l in layers]

        if debug:                                                               #x
            print ("\navailables layers:")                                      #x
            for item in layers:                                                 #x
                print (item)                                                    #x

        if 'VK_LAYER_KHRONOS_validation' in layers:
            layers = ['VK_LAYER_KHRONOS_validation']

        elif 'VK_LAYER_LUNARG_standard_validation' in layers:
            layers = ['VK_LAYER_LUNARG_standard_validation']

        else:
            layers = []

        extensions = ['VK_KHR_surface', 'VK_EXT_debug_report']

    #   print (self.wm_info.subsystem, SDL_SYSWM_WINDOWS, SDL_SYSWM_X11, SDL_SYSWM_WAYLAND)  #x

        if self.wm_info.subsystem ==  SDL_SYSWM_WINDOWS:
            extensions.append ('VK_KHR_win32_surface')

        elif self.wm_info.subsystem ==  SDL_SYSWM_X11:
            extensions.append ('VK_KHR_xlib_surface')

        elif self.wm_info.subsystem ==  SDL_SYSWM_WAYLAND:
            extensions.append ('VK_KHR_wayland_surface')

        else:
            raise Exception (f"Error: Platform not supported: {SDL_GetError ()}\n")

        if debug:                                                               #x
            print ("\navailables extensions:")                                  #x
            for item in extensions:                                             #x
                print (item)                                                    #x

        createInfo = VkInstanceCreateInfo (
            sType                   = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            flags                   = 0,
            pApplicationInfo        = appInfo,
            enabledExtensionCount   = len (extensions),
            ppEnabledExtensionNames = extensions,
            enabledLayerCount       = len (layers),
            ppEnabledLayerNames     = layers)

        self.instance = vkCreateInstance (createInfo, None)
        self.layers   = layers


    def create_logical_device_and_queues (self):
        #only use the extensions necessary
        extensions = [VK_KHR_SWAPCHAIN_EXTENSION_NAME]

        queues_create_info = [VkDeviceQueueCreateInfo (
            sType            = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            queueFamilyIndex = k,
            queueCount       = 1,
            pQueuePriorities = [1],
            flags            = 0) for k in {self.queue_graphic_index, self.queue_present_index}]

        device_create_info = VkDeviceCreateInfo (
            sType                  = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            pQueueCreateInfos      = queues_create_info,
            queueCreateInfoCount   = len (queues_create_info),
            pEnabledFeatures       = self.physical_devices_features[self.physical_device],
            flags                  = 0,
            enabledLayerCount      = len (self.layers),
            ppEnabledLayerNames    = self.layers,
            enabledExtensionCount  = len (extensions),
            ppEnabledExtensionNames = extensions)

        self.logical_device = vkCreateDevice (self.physical_device, device_create_info, None)

        self.graphic_queue = vkGetDeviceQueue (
            device           = self.logical_device,
            queueFamilyIndex = self.queue_graphic_index,
            queueIndex       = 0)

        self.presentation_queue = vkGetDeviceQueue (
            device           = self.logical_device,
            queueFamilyIndex = self.queue_present_index,
            queueIndex       = 0)

        if debug:                                                               #x
            print ("\nLogical device and graphic queue successfully created\n") #x


    def create_render_pass (self):
        color_attachement = VkAttachmentDescription (
            flags          = 0,
            format         = self.surface_format.format,
            samples        = VK_SAMPLE_COUNT_1_BIT,
            loadOp         = VK_ATTACHMENT_LOAD_OP_CLEAR,
            storeOp        = VK_ATTACHMENT_STORE_OP_STORE,
            stencilLoadOp  = VK_ATTACHMENT_LOAD_OP_DONT_CARE,
            stencilStoreOp = VK_ATTACHMENT_STORE_OP_DONT_CARE,
            initialLayout  = VK_IMAGE_LAYOUT_UNDEFINED,
            finalLayout    = VK_IMAGE_LAYOUT_PRESENT_SRC_KHR)

        color_attachement_reference = VkAttachmentReference (
            attachment = 0,
            layout     = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL)

        sub_pass = VkSubpassDescription (
            flags                   = 0,
            pipelineBindPoint       = VK_PIPELINE_BIND_POINT_GRAPHICS,
            inputAttachmentCount    = 0,
            pInputAttachments       = None,
            pResolveAttachments     = None,
            pDepthStencilAttachment = None,
            preserveAttachmentCount = 0,
            pPreserveAttachments    = None,
            colorAttachmentCount    = 1,
            pColorAttachments       = [color_attachement_reference])

        dependency = VkSubpassDependency (
            dependencyFlags = 0,
            srcSubpass      = VK_SUBPASS_EXTERNAL,
            dstSubpass      = 0,
            srcStageMask    = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            srcAccessMask   = 0,
            dstStageMask    = VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT,
            dstAccessMask   = VK_ACCESS_COLOR_ATTACHMENT_READ_BIT | VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT)

        render_pass_create  = VkRenderPassCreateInfo (
            flags           = 0,
            sType           = VK_STRUCTURE_TYPE_RENDER_PASS_CREATE_INFO,
            attachmentCount = 1,
            pAttachments    = [color_attachement],
            subpassCount    = 1,
            pSubpasses      = [sub_pass],
            dependencyCount = 1,
            pDependencies   = [dependency])

        self.render_pass = vkCreateRenderPass (self.logical_device, render_pass_create, None)


    def create_semaphore (self):
        semaphore_create_info = VkSemaphoreCreateInfo (
            sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO,
            flags = 0)

        semaphore_image_available = vkCreateSemaphore (self.logical_device, semaphore_create_info, None)
        semaphore_render_finished = vkCreateSemaphore (self.logical_device, semaphore_create_info, None)

        vkAcquireNextImageKHR = vkGetInstanceProcAddr (self.instance, "vkAcquireNextImageKHR")
        vkQueuePresentKHR     = vkGetInstanceProcAddr (self.instance, "vkQueuePresentKHR")

        wait_semaphores   = [semaphore_image_available]
        wait_stages       = [VK_PIPELINE_STAGE_COLOR_ATTACHMENT_OUTPUT_BIT]
        signal_semaphores = [semaphore_render_finished]

        self.submit_create_info = VkSubmitInfo (
            sType                = VK_STRUCTURE_TYPE_SUBMIT_INFO,
            waitSemaphoreCount   = len (wait_semaphores),
            pWaitSemaphores      = wait_semaphores,
            pWaitDstStageMask    = wait_stages,
            commandBufferCount   = 1,
            pCommandBuffers      = [self.command_buffers[0]],
            signalSemaphoreCount = len (signal_semaphores),
            pSignalSemaphores    = signal_semaphores)

        self.present_create_info = VkPresentInfoKHR (
            sType              = VK_STRUCTURE_TYPE_PRESENT_INFO_KHR,
            waitSemaphoreCount = 1,
            pWaitSemaphores    = signal_semaphores,
            swapchainCount     = 1,
            pSwapchains        = [self.swapchain],
            pImageIndices      = [0],
            pResults           = None)

    #   Optimization to avoid creating a new array each time
        self.submit_list = ffi.new ('VkSubmitInfo[1]', [self.submit_create_info])
        self.semaphore_image_available = semaphore_image_available
        self.semaphore_render_finished = semaphore_render_finished


    def create_surface (self):
        surface_mapping = {
            SDL_SYSWM_X11:     self.surface_xlib,
            SDL_SYSWM_WAYLAND: self.surface_wayland,
            SDL_SYSWM_WINDOWS: self.surface_win32
        }

        self.surface = surface_mapping[self.wm_info.subsystem] ()


    def create_swapchain (self):
        vkGetPhysicalDeviceSurfaceCapabilitiesKHR = vkGetInstanceProcAddr (self.instance, "vkGetPhysicalDeviceSurfaceCapabilitiesKHR")
        vkGetPhysicalDeviceSurfaceFormatsKHR      = vkGetInstanceProcAddr (self.instance, "vkGetPhysicalDeviceSurfaceFormatsKHR")
        vkGetPhysicalDeviceSurfacePresentModesKHR = vkGetInstanceProcAddr (self.instance, "vkGetPhysicalDeviceSurfacePresentModesKHR")

        surface_capabilities  = vkGetPhysicalDeviceSurfaceCapabilitiesKHR (physicalDevice = self.physical_device, surface = self.surface)
        surface_formats       = vkGetPhysicalDeviceSurfaceFormatsKHR      (physicalDevice = self.physical_device, surface = self.surface)
        surface_present_modes = vkGetPhysicalDeviceSurfacePresentModesKHR (physicalDevice = self.physical_device, surface = self.surface)

        if not surface_formats or not surface_present_modes:
            raise Exception (f"Error: No available swapchain: {SDL_GetError ()}")

        surface_format = self.get_surface_format (surface_formats)
        present_mode   = self.get_surface_present_mode (surface_present_modes)
        extent         = self.get_swap_extent (surface_capabilities)
        imageCount     = surface_capabilities.minImageCount + 1;

        if surface_capabilities.maxImageCount > 0 and imageCount > surface_capabilities.maxImageCount:
            imageCount = surface_capabilities.maxImageCount

        if self.queue_graphic_index != self.queue_present_index:
            imageSharingMode      = VK_SHARING_MODE_CONCURRENT
            queueFamilyIndexCount = 2
            pQueueFamilyIndices   = [self.queue_graphic_index, self.queue_present_index]

        else:
            imageSharingMode      = VK_SHARING_MODE_EXCLUSIVE
            queueFamilyIndexCount = 0
            pQueueFamilyIndices   = None

        vkCreateSwapchainKHR    = vkGetInstanceProcAddr (self.instance, 'vkCreateSwapchainKHR')
        vkDestroySwapchainKHR   = vkGetInstanceProcAddr (self.instance, 'vkDestroySwapchainKHR')
        vkGetSwapchainImagesKHR = vkGetInstanceProcAddr (self.instance, 'vkGetSwapchainImagesKHR')

        swapchain_create_info = VkSwapchainCreateInfoKHR (
            sType                 = VK_STRUCTURE_TYPE_SWAPCHAIN_CREATE_INFO_KHR,
            flags                 = 0,
            surface               = self.surface,
            minImageCount         = imageCount,
            imageFormat           = surface_format.format,
            imageColorSpace       = surface_format.colorSpace,
            imageExtent           = extent,
            imageArrayLayers      = 1,
            imageUsage            = VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT,
            imageSharingMode      = imageSharingMode,
            queueFamilyIndexCount = queueFamilyIndexCount,
            pQueueFamilyIndices   = pQueueFamilyIndices,
            compositeAlpha        = VK_COMPOSITE_ALPHA_OPAQUE_BIT_KHR,
            presentMode           = present_mode,
            clipped               = VK_TRUE,
            oldSwapchain          = None,
            preTransform          = surface_capabilities.currentTransform)

        swapchain = vkCreateSwapchainKHR (self.logical_device, swapchain_create_info, None)
        swapchain_images = vkGetSwapchainImagesKHR (self.logical_device, swapchain)

    #   Create an image view for each image in the swapchain
        image_views = []
        for image in swapchain_images:
            subresourceRange = VkImageSubresourceRange (
                aspectMask     = VK_IMAGE_ASPECT_COLOR_BIT,
                baseMipLevel   = 0,
                levelCount     = 1,
                baseArrayLayer = 0,
                layerCount     = 1)

            components = VkComponentMapping (
                r = VK_COMPONENT_SWIZZLE_IDENTITY,
                g = VK_COMPONENT_SWIZZLE_IDENTITY,
                b = VK_COMPONENT_SWIZZLE_IDENTITY,
                a = VK_COMPONENT_SWIZZLE_IDENTITY)

            imageview_create_info = VkImageViewCreateInfo (
                sType            = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
                image            = image,
                flags            = 0,
                viewType         = VK_IMAGE_VIEW_TYPE_2D,
                format           = surface_format.format,
                components       = components,
                subresourceRange = subresourceRange)

            image_views.append (vkCreateImageView (self.logical_device, imageview_create_info, None))

        if debug:                                                                       #x
            print (f'selected format: {surface_format.format}')                         #x
            print (f'{len (surface_present_modes)} available swapchain present modes')  #x
            print (f"{len (image_views)} images view created\n")                        #x

        self.surface_format = surface_format
        self.extent         = extent
        self.image_views    = image_views
        self.swapchain      = swapchain


    def draw_frame (self):
        try:
            vkAcquireNextImageKHR = vkGetInstanceProcAddr (self.instance, "vkAcquireNextImageKHR")
            image_index = vkAcquireNextImageKHR (self.logical_device, self.swapchain, UINT64_MAX, self.semaphore_image_available, None)

            self.submit_create_info.pCommandBuffers[0] = self.command_buffers[image_index]
            vkQueueSubmit (self.graphic_queue, 1, self.submit_list, None)

            self.present_create_info.pImageIndices[0] = image_index
            vkQueuePresentKHR = vkGetInstanceProcAddr (self.instance, "vkQueuePresentKHR")
            vkQueuePresentKHR (self.presentation_queue, self.present_create_info)

            # Fix #55 but downgrade performance -1000FPS)
            vkQueueWaitIdle (self.presentation_queue)

        except VkNotReady:
            print ('Vulkan is not ready!')
            return


    def get_surface_format (self, formats):
        for f in formats:
            if f.format == VK_FORMAT_UNDEFINED:
                return  f

            if (f.format == VK_FORMAT_B8G8R8A8_UNORM and f.colorSpace == VK_COLOR_SPACE_SRGB_NONLINEAR_KHR):
                return f

        return formats[0]


    def get_surface_present_mode (self, present_modes):
        for p in present_modes:
            if p == VK_PRESENT_MODE_MAILBOX_KHR:
                return p

        return VK_PRESENT_MODE_FIFO_KHR;


    def get_swap_extent (self, capabilities):
        uint32_max = 4294967295
        if capabilities.currentExtent.width !=  uint32_max:
            return VkExtent2D (width = capabilities.currentExtent.width, height = capabilities.currentExtent.height)

        width  = max (capabilities.minImageExtent.width,  min (capabilities.maxImageExtent.width, WIDTH))
        height = max (capabilities.minImageExtent.height, min (capabilities.maxImageExtent.height, HEIGHT))

        actualExtent = VkExtent2D (width = width, height = height);
        return actualExtent


    def initWindow (self):
        if SDL_Init (SDL_INIT_VIDEO) !=  0:
            raise Exception (f"Error: Failed to initialize SDL2: {SDL_GetError ()}")
            sys.exit (1)

        self.window = SDL_CreateWindowFrom (self.parent.winfo_id ())            #wbh
        if not self.window:
            raise Exception (f"Error: Failed to create SDL2 window: {SDL_GetError ()}")
            sys.exit (1)

        self.wm_info = SDL_SysWMinfo ()
        SDL_VERSION (self.wm_info.version)
        result = SDL_GetWindowWMInfo (self.window, ctypes.byref (self.wm_info))

        if debug:                                                                                                                       #x
            print (f"Result: {result}, SDL2 {self.wm_info.version.major}.{self.wm_info.version.minor}.{self.wm_info.version.patch}")    #x


    def load_spirv_shaders (self):
    #   print ("load_spirv_shaders ()")                                         #tbr

        path = os.path.dirname (os.path.abspath (__file__))
        with open (os.path.join (path, "vert.spv"), 'rb') as f:
            vert_shader_spirv = f.read ()

        with open (os.path.join (path, "frag.spv"), 'rb') as f:
            frag_shader_spirv = f.read ()

    #   Create shaders
        vert_shader_create_info = VkShaderModuleCreateInfo (
            sType    = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
            flags    = 0,
            codeSize = len (vert_shader_spirv),
            pCode    = vert_shader_spirv)

        vulkan_bug_workaround = self.surface_format.format

    #   print (f'selected format 1: {self.surface_format.format}')              #tbr
        vert_shader_module = vkCreateShaderModule (self.logical_device, vert_shader_create_info, None)  # <-- sets surface_format.format to 0
    #   print (f'selected format 2: {self.surface_format.format}')              #tbr

    #   self.surface_format.format = vulkan_bug_workaround                      #tbr
    #   print (f'selected format 3: {self.surface_format.format}')              #tbr

        frag_shader_create_info = VkShaderModuleCreateInfo (
            sType    = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
            flags    = 0,
            codeSize = len (frag_shader_spirv),
            pCode    = frag_shader_spirv)

    #   print (f'selected format 4: {self.surface_format.format}')              #tbr
        frag_shader_module = vkCreateShaderModule (self.logical_device, frag_shader_create_info, None)
    #   print (f'selected format 5: {self.surface_format.format}')              #tbr

        self.surface_format.format = vulkan_bug_workaround

        # Create shader stage
        self.vert_stage_create  = VkPipelineShaderStageCreateInfo (
            sType               = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            stage               = VK_SHADER_STAGE_VERTEX_BIT,
            module              = vert_shader_module,
            flags               = 0,
            pSpecializationInfo = None,
            pName               = 'main')

        self.frag_stage_create  = VkPipelineShaderStageCreateInfo (
            sType               = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
            stage               = VK_SHADER_STAGE_FRAGMENT_BIT,
            module              = frag_shader_module,
            flags               = 0,
            pSpecializationInfo = None,
            pName               = 'main')

        self.vert_shader_module = vert_shader_module
        self.frag_shader_module = frag_shader_module


    def poll (self):                        # Instead of Main loop              #wbh
        self.draw_frame ()                                                      #wbh
        self.poll_id = self.canvas.after (20, self.poll) # 50 frames per second #wbh


    def select_physical_device (self):
        physical_devices               = vkEnumeratePhysicalDevices (self.instance)
        self.physical_devices_features = {physical_device: vkGetPhysicalDeviceFeatures   (physical_device) for physical_device in physical_devices}
        physical_devices_properties    = {physical_device: vkGetPhysicalDeviceProperties (physical_device) for physical_device in physical_devices}
        self.physical_device           = physical_devices[0]

        if debug:                                                                                       #x
            print ("\navailables devices:")                                                             #x
            for item in [p.deviceName for p in physical_devices_properties.values ()]:                  #x
                print (item)                                                                            #x

            print (f"\nselected device: {physical_devices_properties[self.physical_device].deviceName}")#x


    def select_queue_family (self):
        vkGetPhysicalDeviceSurfaceSupportKHR = vkGetInstanceProcAddr (self.instance, 'vkGetPhysicalDeviceSurfaceSupportKHR')
        queue_families = vkGetPhysicalDeviceQueueFamilyProperties (physicalDevice = self.physical_device)
        print (f"\n{len (queue_families)} available queue family")              #x

        self.queue_graphic_index = -1
        self.queue_present_index = -1

        for k, queue_family in enumerate (queue_families):
        #   Currently, we set present index like graphic index
            support_present = vkGetPhysicalDeviceSurfaceSupportKHR (
                physicalDevice   = self.physical_device,
                queueFamilyIndex = k,
                surface          = self.surface)

            if (queue_family.queueCount > 0 and queue_family.queueFlags & VK_QUEUE_GRAPHICS_BIT):
                self.queue_graphic_index = k
                self.queue_present_index = k

        if debug:                                                                                                                           #x
            print (f"indices of selected queue families, graphic: {self.queue_graphic_index}, presentation: {self.queue_present_index}")    #x


    def setup_debug_messenger (self):
        vkCreateDebugReportCallbackEXT  = vkGetInstanceProcAddr (self.instance, "vkCreateDebugReportCallbackEXT")

        def debugCallback (*args):
            print ('DEBUG: ' + args[5] + ' ' + args[6])
            return 0

        createInfo = VkDebugReportCallbackCreateInfoEXT (
            sType       = VK_STRUCTURE_TYPE_DEBUG_REPORT_CALLBACK_CREATE_INFO_EXT,
            flags       = VK_DEBUG_REPORT_ERROR_BIT_EXT | VK_DEBUG_REPORT_WARNING_BIT_EXT,
            pfnCallback = debugCallback)

        self.callback = vkCreateDebugReportCallbackEXT (self.instance, createInfo, None)


    def shut_down_vulkan (self):
    #   print ("shut_down_vulkan ()", flush = True)                             #tbr

    #   Clean everything
        vkDestroySemaphore (self.logical_device, self.semaphore_image_available, None)
        vkDestroySemaphore (self.logical_device, self.semaphore_render_finished, None)
        vkDestroyCommandPool (self.logical_device, self.command_pool, None)

        for f in self.framebuffers:
            vkDestroyFramebuffer (self.logical_device, f, None)

        vkDestroyPipeline (self.logical_device, self.pipeline, None)
        vkDestroyPipelineLayout (self.logical_device, self.pipeline_layout, None)
        vkDestroyRenderPass (self.logical_device, self.render_pass, None)
        vkDestroyShaderModule (self.logical_device, self.frag_shader_module, None)
        vkDestroyShaderModule (self.logical_device, self.vert_shader_module, None)

        for k in self.image_views:
            vkDestroyImageView (self.logical_device, k, None)

        vkDestroySwapchainKHR           = vkGetInstanceProcAddr (self.instance, "vkDestroySwapchainKHR")
        vkDestroySurfaceKHR             = vkGetInstanceProcAddr (self.instance, "vkDestroySurfaceKHR")
        vkDestroyDebugReportCallbackEXT = vkGetInstanceProcAddr (self.instance, "vkDestroyDebugReportCallbackEXT")

        vkDestroySwapchainKHR (self.logical_device, self.swapchain, None)
        vkDestroyDevice (self.logical_device, None)
        vkDestroySurfaceKHR (self.instance, self.surface, None)
        vkDestroyDebugReportCallbackEXT (self.instance, self.callback, None)
        vkDestroyInstance (self.instance, None)

        self.canvas.after_cancel (self.poll_id)                                 #wbh
        SDL_DestroyWindow (self.window)                                         #wbh
        SDL_Quit ()                                                             #wbh


    def surface_wayland (self):
        print ("\nCreate wayland surface")                                      #tbr
        vkCreateWaylandSurfaceKHR = vkGetInstanceProcAddr (self.instance, "vkCreateWaylandSurfaceKHR")
        surface_create = VkWaylandSurfaceCreateInfoKHR (
            sType   = VK_STRUCTURE_TYPE_WAYLAND_SURFACE_CREATE_INFO_KHR,
            display = self.wm_info.info.wl.display,
            surface = self.wm_info.info.wl.surface,
            flags   = 0)

        return vkCreateWaylandSurfaceKHR (self.instance, surface_create, None)


    def surface_win32 (self):
        def get_instance (hWnd):
            """Hack needed before SDL 2.0.6"""
            from cffi import FFI
            _ffi = FFI ()
            _ffi.cdef ('long __stdcall GetWindowLongA (void* hWnd, int nIndex);')
            _lib = _ffi.dlopen ('User32.dll')

            return _lib.GetWindowLongA (_ffi.cast ('void*', hWnd), -6)

        print ("\nCreate windows surface")                                      #tbr
        vkCreateWin32SurfaceKHR = vkGetInstanceProcAddr (self.instance, "vkCreateWin32SurfaceKHR")
        surface_create = VkWin32SurfaceCreateInfoKHR (
            sType     = VK_STRUCTURE_TYPE_WIN32_SURFACE_CREATE_INFO_KHR,
            hinstance = get_instance (self.wm_info.info.win.window),
            hwnd      = self.wm_info.info.win.window,
            flags     = 0)

        return vkCreateWin32SurfaceKHR (self.instance, surface_create, None)


    def surface_xlib (self):
        print ("\nCreate Xlib surface")                                         #tbr
        vkCreateXlibSurfaceKHR = vkGetInstanceProcAddr (self.instance, "vkCreateXlibSurfaceKHR")
        surface_create = VkXlibSurfaceCreateInfoKHR (
            sType      = VK_STRUCTURE_TYPE_XLIB_SURFACE_CREATE_INFO_KHR,
            dpy        = self.wm_info.info.x11.display,
            window     = self.wm_info.info.x11.window,
            flags      = 0)

        return vkCreateXlibSurfaceKHR (self.instance, surface_create, None)


#---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---
class App (tk.Tk):
    def __init__ (self):
        super ().__init__ ()
        self.resizable (width = False, height = False)

    #   print ("Threaded:", tk.Tcl ().eval ('set tcl_platform(threaded)'))   # https://tkdocs.com/tutorial/eventloop.html

        self.tkvkn = TkVkn (self)


#---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---
if __name__ == "__main__":
    try:
        app = App ()
        app.mainloop ()

    finally:
        app.tkvkn.shut_down_vulkan ()       # Clean everything
