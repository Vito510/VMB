class Test_Commands(commands.Cog):
    """Test commands"""
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def test_run(self, ctx):
        start_time_total = time.time()
        success = 0
        fail = 0
        click.echo('Running tests')
        click.secho('\nTesting cache clearing',fg='yellow')
        try:
            await clear_cache(ctx)
            click.secho('Cleared cache test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed to clear cache: '+str(e),fg="red")
            fail += 1

        click.secho('\nTesting youtube search',fg='yellow')
        try:
            x = functions.youtube_search("nelward ghost")
            click.secho(x[0]+" "+x[1],fg="green")
            click.secho('Youtube search test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed to search youtube: '+str(e),fg="red")
            fail += 1

        click.secho('\nTesting [YT-API-v3] search',fg='yellow')
        try:
            x = functions.youtube_searchGOOD("nelward ghost")
            click.secho(x[0]+" "+x[1],fg="green")
            click.secho('[YT-API-v3] search test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed [YT-API-v3] search: '+str(e),fg="red")
            fail += 1

        click.secho('\nTesting join command',fg='yellow')
        try:
            await join(ctx)
            click.secho('Join command test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed to join: '+str(e),fg="red")
            fail += 1

        click.secho('\nTesting yt command',fg='yellow')
        try:
            await Media_Controls.yt(self,ctx,search="nelward ghost")
            click.secho('yt command test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed yt command test: '+str(e),fg="red")
            fail += 1

        click.secho('\nTesting pause command',fg='yellow')
        try:
            await Media_Controls.pause(self,ctx)
            click.secho('Pause command test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed pause command test: '+str(e),fg="red")
            fail += 1
        
        click.secho('\nTesting resume command',fg='yellow')
        try:
            await Media_Controls.resume(self,ctx)
            click.secho('Resume command test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed resume command test: '+str(e),fg="red")
            fail += 1

        click.secho('\nTesting clear command',fg='yellow')
        try:
            await Media_Controls.clear(self,ctx)
            click.secho('Clear command test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed clear command test: '+str(e),fg="red")
            fail += 1
        
        click.secho('\nTesting leave command',fg='yellow')
        try:
            await leave(ctx)
            click.secho('Leave command test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed leave command test: '+str(e),fg="red")
            fail += 1

        click.secho('\nTesting yt command (playlist) + autoconnect',fg='yellow')
        try:
            await Media_Controls.yt(self,ctx,search="https://www.youtube.com/playlist?list=PLmeBqWgbwZggUDfsm5u3D_q1pO3v8a3U1")
            click.secho('yt command test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed yt command test: '+str(e),fg="red")
            fail += 1
          
        click.secho('\nTesting auto remove unavailable sources',fg='yellow')
        temp = len(queue)  # save queue length
        await asyncio.sleep(15)
        if temp - len(queue) == 2:
            click.secho('Auto remove unavailable sources test successfull',fg="green")
            success += 1
        else:
            click.secho('Failed auto remove unavailable sources test',fg="red")
            fail += 1

        await Media_Controls.clear(self,ctx)
        await Media_Controls.yt(self,ctx,search="https://www.youtube.com/playlist?list=PLmeBqWgbwZghxvXwj3Dsz2WgWzQSff7xR")

        click.secho('\nTesting skip command',fg='yellow')
        success_s = 0
        fail_s = 0
        start_time = time.time()
        for i in tqdm(range(0,5),bar_format=bf):
            try:
                pre = queue_index
                await Media_Controls.skip(self,ctx,s=True)
                await asyncio.sleep(1)
                post = queue_index
                if pre == post-1:
                    success_s += 1
                else:
                    fail_s += 1
            except Exception as e:
                fail_s += 1
                click.secho('Failed ({}/{}): {}'.format(i+1,5,str(e)),fg="red")

        t = round(time.time()-start_time,3)

        if success_s == 5:
            click.secho('Skip command test successfull ({}/5,{}%) {}ms'.format(success_s,success_s/5*100,t*1000),fg="green")
            success += 1
        else:
            click.secho('Failed skip command test ({}/5,{}%)'.format(success_s,success_s/5*100),fg="red")
            fail += 1

        click.secho('\nTesting back command',fg='yellow')
        success_s = 0
        fail_s = 0
        start_time = time.time()
        for i in tqdm(range(0,5),bar_format=bf):
            try:
                pre = queue_index
                await Media_Controls.back(self,ctx,s=True)
                await asyncio.sleep(1)
                post = queue_index
                if pre == post+1:
                    success_s += 1
                else:
                    fail_s += 1
            except Exception as e:
                fail_s += 1
                click.secho('Failed ({}/{}): {}'.format(i+1,5,str(e)),fg="red")

        t = round(time.time()-start_time,3)

        if success_s == 5:
            click.secho('Back command test successfull ({}/5,{}%) {}ms'.format(success_s,success_s/5*100,t*1000),fg="green")
            success += 1
        else:
            click.secho('Failed back command test ({}/5,{}%)'.format(success_s,success_s/5*100),fg="red")
            fail += 1
        
        click.secho('\nTesting jump command',fg='yellow')
        success_s = 0
        fail_s = 0
        start_time = time.time()
        for i in tqdm(range(0,5),bar_format=bf):
            try:
                jump_amount = random.randint(len(queue)*-1+1,len(queue)-1)
                await Media_Controls.jump(self,ctx,number=jump_amount,s=True)
                await asyncio.sleep(1)
                if queue_index-1 == jump_amount:
                    success_s += 1
                else:
                    fail_s += 1
                    print(queue_index,jump_amount)
            except Exception as e:
                fail_s += 1
                click.secho('Failed ({}/{}): {}'.format(i+1,5,str(e)),fg="red")

        t = round(time.time()-start_time,3)

        if success_s == 5:
            click.secho('Jump command test successfull ({}/5,{}%) {}ms'.format(success_s,success_s/5*100,t*1000),fg="green")
            success += 1
        else:
            click.secho('Failed jump command test ({}/5,{}%)'.format(success_s,success_s/5*100),fg="red")
            fail += 1



        click.secho('\nTesting shuffle command',fg='yellow')
        try:
            pre = queue
            await Media_Controls.shuffle(self,ctx)
            click.secho('Shuffle command test successfull',fg="green")
            success += 1
        except Exception as e:
            click.secho('Failed shuffle command test: '+str(e),fg="red")
            fail += 1

        t = round(time.time()-start_time_total,3)
        
        if success == success+fail:
            click.secho('\nTests successfull ({}/{},{}) {}ms'.format(success,success+fail,success/(success+fail)*100,t*1000),fg="green")
        else:
            click.secho('\nTests successfull ({}/{},{}) {}ms'.format(success,success+fail,success/(success+fail)*100,t*1000),fg="yellow")

  